import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, Row, Col, Typography, Select, Button, Spin, Empty, Alert } from 'antd';
import Plot from 'react-plotly.js';
import ApiService from '../services/ApiService'; // Keep ApiService for getParameters

const { Title } = Typography;
const { Option } = Select;

// Helper to check if a value is numeric
const isNumeric = (value) => value !== null && !isNaN(parseFloat(value)) && isFinite(value);

const ChartAnalysis = () => {
  const { symbol } = useParams();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [parametersLoading, setParametersLoading] = useState(false);
  const [parameterSets, setParameterSets] = useState([]);
  const [selectedParameterSet, setSelectedParameterSet] = useState('default');
  const [period, setPeriod] = useState('1y');
  const [chartData, setChartData] = useState([]); // Store array of data points
  const [error, setError] = useState(null);

  // Load available parameter sets
  useEffect(() => {
    const fetchParameters = async () => {
      try {
        setParametersLoading(true);
        const data = await ApiService.getParameters(); // Use ApiService here
        setParameterSets(data);
      } catch (error) {
        console.error('Error fetching parameter sets:', error);
        setError(t('error_fetching_parameters'));
      } finally {
        setParametersLoading(false);
      }
    };
    fetchParameters();
  }, [t]);

  // Fetch chart data function
  const fetchChartData = useCallback(async () => {
    if (!symbol) return;
    try {
      setLoading(true);
      setError(null);
      setChartData([]); // Clear previous data

      // Construct API URL (assuming backend runs on port 5000)
      // TODO: Use environment variable for API base URL
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/chart-data/${symbol}?parameter_set=${selectedParameterSet}&period=${period}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      if (data && data.data) {
        setChartData(data.data); // Store the array of data points
      } else {
        setChartData([]);
      }

    } catch (error) {
      console.error(`Error fetching chart data for ${symbol}:`, error);
      setError(`${t('error_fetching_chart_data')}: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [symbol, selectedParameterSet, period, t]);

  // Fetch data when symbol, parameter set, or period changes
  useEffect(() => {
    fetchChartData();
  }, [fetchChartData]); // Use the memoized fetch function

  const handleParameterChange = (value) => {
    setSelectedParameterSet(value);
  };

  const handlePeriodChange = (value) => {
    setPeriod(value);
  };

  // Prepare data and layout for Plotly
  const preparePlotData = () => {
    if (!chartData || chartData.length === 0) return [];

    const dates = chartData.map(d => d.Date);
    const opens = chartData.map(d => d.Open);
    const highs = chartData.map(d => d.High);
    const lows = chartData.map(d => d.Low);
    const closes = chartData.map(d => d.Close);

    const plotTraces = [];

    // 1. Candlestick Trace (if OHLC data exists)
    if (opens.some(isNumeric) && highs.some(isNumeric) && lows.some(isNumeric) && closes.some(isNumeric)) {
      plotTraces.push({
        x: dates,
        open: opens,
        high: highs,
        low: lows,
        close: closes,
        type: 'candlestick',
        name: symbol || 'Price',
        xaxis: 'x',
        yaxis: 'y1', // Main price axis
        increasing: { line: { color: 'green' } },
        decreasing: { line: { color: 'red' } },
      });
    } else if (closes.some(isNumeric)) { // Fallback to line chart if only Close exists
       plotTraces.push({
        x: dates,
        y: closes,
        type: 'scatter',
        mode: 'lines',
        name: symbol || 'Close Price',
        yaxis: 'y1',
        line: { color: 'black' }
      });
    }


    // 2. Indicator Traces (dynamically add based on available data)
    const indicatorKeys = Object.keys(chartData[0] || {}).filter(
      key => !['Date', 'Open', 'High', 'Low', 'Close', 'Volume'].includes(key) && chartData.some(d => isNumeric(d[key]))
    );

    // Group indicators for subplots (example grouping)
    const subplotIndicators = {
      y2: ['RSI', 'STOCH_K', 'STOCH_D', 'ADX', 'RSI7'], // Oscillators typically 0-100
      y3: ['MACD', 'MACD_Signal', 'MACD_HF', 'MACD_HF_Signal'], // MACD-like indicators
      y4: ['BB_High', 'BB_Mid', 'BB_Low', 'BB_Tight_High', 'BB_Tight_Mid', 'BB_Tight_Low', 'BB_Wide_High', 'BB_Wide_Mid', 'BB_Wide_Low', 'Ichimoku_Tenkan', 'Ichimoku_Kijun', 'Ichimoku_SpanA', 'Ichimoku_SpanB', 'Ichimoku_Chikou', 'SAR'], // Overlays / Bands / Ichimoku / SAR - plot on main or separate axis if needed
      y5: ['OBV', 'OBV_MA'] // Volume based
    };
    const mainPlotIndicators = ['SMA', 'EMA']; // Indicators to plot on main price axis (check prefixes)

    indicatorKeys.forEach(key => {
      const values = chartData.map(d => d[key]);
      let assignedSubplot = null;
      let traceType = 'scatter';
      let traceMode = 'lines';
      let traceFill = undefined;
      let traceFillColor = undefined;
      let traceLine = undefined;

      // Assign to subplot or main plot
      if (mainPlotIndicators.some(prefix => key.startsWith(prefix))) {
        assignedSubplot = 'y1'; // Plot SMAs/EMAs on main price axis
      } else {
        for (const [axis, indicators] of Object.entries(subplotIndicators)) {
          if (indicators.includes(key) || indicators.some(prefix => key.startsWith(prefix))) {
            assignedSubplot = axis;
            break;
          }
        }
      }

      // Special handling for certain indicators
      if (key.includes('Histogram')) {
          traceType = 'bar';
          traceMode = undefined; // Bars don't use mode
          // Basic coloring for histogram bars
          const colors = values.map(v => v >= 0 ? 'rgba(0, 128, 0, 0.5)' : 'rgba(255, 0, 0, 0.5)');
          traceLine = { color: colors }; // Use marker color for bars
      } else if (key.startsWith('BB_') || key.startsWith('Ichimoku_Span')) {
          // Basic styling for bands/cloud
          if (key.endsWith('_High') || key === 'Ichimoku_SpanA') traceLine = { color: 'rgba(0, 0, 255, 0.5)', width: 1 };
          else if (key.endsWith('_Low') || key === 'Ichimoku_SpanB') traceLine = { color: 'rgba(0, 0, 255, 0.5)', width: 1 };
          else if (key.endsWith('_Mid')) traceLine = { color: 'rgba(0, 0, 255, 0.5)', dash: 'dash', width: 1 };
          else traceLine = { width: 1 }; // Default line style

          // Fill for Bollinger Bands and Ichimoku Cloud
          if (key === 'BB_Low') {
              traceFill = 'tonexty'; // Fill to the BB_High trace (assuming BB_High is added before BB_Low)
              traceFillColor = 'rgba(0, 0, 255, 0.1)';
          }
          // Ichimoku fill requires SpanA and SpanB, handled separately if needed or approximated
      } else if (key === 'SAR') {
          traceType = 'scatter';
          traceMode = 'markers';
          traceLine = { color: 'purple', size: 3 };
      }


      if (assignedSubplot) {
        plotTraces.push({
          x: dates,
          y: values,
          type: traceType,
          mode: traceMode,
          name: key,
          yaxis: assignedSubplot,
          line: traceLine,
          fill: traceFill,
          fillcolor: traceFillColor,
          marker: traceType === 'bar' ? { color: traceLine?.color } : undefined, // Apply color to markers for bars
        });
      }
      // Else: Indicator not explicitly assigned to a subplot, could be plotted on main or ignored
    });

    return plotTraces;
  };

  const preparePlotLayout = () => {
    // Basic layout, adjust domain for subplots
    const layout = {
      title: `${symbol} - ${t(`parameter_sets.${selectedParameterSet}`)} (${period})`,
      height: 800,
      showlegend: true,
      legend: { orientation: "h", yanchor: "bottom", y: 1.02, xanchor: "right", x: 1 },
      xaxis: {
        anchor: 'y1', // Anchor main x-axis to the bottom plot
        domain: [0, 1], // Full width
        rangeslider: { visible: false }, // Hide range slider for simplicity now
        type: 'date'
      },
      yaxis: { // y1 - Main Price Axis
        domain: [0.5, 1], // Top 50%
        title: 'Price'
      },
      yaxis2: { // y2 - Subplot 1 (e.g., RSI)
        domain: [0.35, 0.48], // Below price
        title: 'Oscillator'
      },
      yaxis3: { // y3 - Subplot 2 (e.g., MACD)
        domain: [0.20, 0.33], // Below subplot 1
        title: 'MACD'
      },
      yaxis4: { // y4 - Subplot 3 (e.g., Bands/Overlays if not on main)
         domain: [0.05, 0.18], // Below subplot 2
         title: 'Overlays/Vol'
      },
      // yaxis5: { // y5 - Subplot 4 (e.g., Volume/OBV)
      //    domain: [0, 0.13], // Bottom plot
      //    title: 'Volume/OBV'
      // },
      grid: {
          rows: 4, // Adjust based on number of yaxes used
          columns: 1,
          pattern: 'independent' // Each subplot has its own scale
      },
      margin: { l: 50, r: 50, t: 80, b: 50 },
      autosize: true,
    };

    // Add shapes for RSI levels if RSI exists
    const rsiExists = chartData.length > 0 && chartData[0].hasOwnProperty('RSI');
    if (rsiExists) {
        layout.shapes = [
            { type: 'line', xref: 'paper', x0: 0, x1: 1, yref: 'y2', y0: 70, y1: 70, line: { color: 'red', width: 1, dash: 'dash' } },
            { type: 'line', xref: 'paper', x0: 0, x1: 1, yref: 'y2', y0: 30, y1: 30, line: { color: 'green', width: 1, dash: 'dash' } }
        ];
    }


    return layout;
  };


  const renderContent = () => {
    if (loading) {
      return (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
          <p>{t('chart_analysis.loading_chart')}</p>
        </div>
      );
    }

    if (error) {
      return (
        <Alert
          message={error}
          description={t('error_description')}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={fetchChartData}>
              {t('retry')}
            </Button>
          }
        />
      );
    }

    if (!chartData || chartData.length === 0) {
      return <Empty description={t('no_data')} />;
    }

    const plotData = preparePlotData();
    const plotLayout = preparePlotLayout();

    return (
       <Plot
        data={plotData}
        layout={plotLayout}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler={true}
        config={{ responsive: true }} // Make chart responsive
      />
    );
  };

  return (
    <div className="chart-analysis-container">
      <Title level={2}>
        {symbol} - {t('chart_analysis.title')}
      </Title>

      <Card className="mb-4">
        <Row gutter={16} align="middle">
          <Col xs={24} md={6}>
            <Select
              placeholder={t('chart_analysis.select_parameter')}
              onChange={handleParameterChange}
              value={selectedParameterSet}
              style={{ width: '100%' }}
              loading={parametersLoading}
            >
              {parameterSets.map(param => (
                <Option key={param} value={param}>
                  {/* Attempt to translate parameter set names */}
                  {t(`parameter_sets.${param}`, param)}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} md={6}>
            <Select
              placeholder={t('chart_analysis.select_period')}
              onChange={handlePeriodChange}
              value={period}
              style={{ width: '100%' }}
            >
              <Option value="1mo">{t('chart_analysis.periods.1mo')}</Option>
              <Option value="3mo">{t('chart_analysis.periods.3mo')}</Option>
              <Option value="6mo">{t('chart_analysis.periods.6mo')}</Option>
              <Option value="1y">{t('chart_analysis.periods.1y')}</Option>
              <Option value="2y">{t('chart_analysis.periods.2y')}</Option>
              <Option value="5y">{t('chart_analysis.periods.5y')}</Option>
            </Select>
          </Col>
          <Col xs={24} md={12}>
            {/* Button now implicitly triggers refetch via useEffect */}
             <Button
              type="primary"
              onClick={fetchChartData} // Explicitly allow manual refresh
              loading={loading}
              style={{ marginRight: '10px' }}
            >
              {t('chart_analysis.refresh_chart')}
            </Button>

            <Button
              onClick={() => window.open(`/reports/${symbol}?parameter_set=${selectedParameterSet}`, '_blank')}
            >
              {t('chart_analysis.view_report')}
            </Button>
          </Col>
        </Row>
      </Card>

      <Card className="chart-display" style={{ height: '850px' /* Ensure card has height */ }}>
        {renderContent()}
      </Card>
    </div>
  );
};

export default ChartAnalysis;
