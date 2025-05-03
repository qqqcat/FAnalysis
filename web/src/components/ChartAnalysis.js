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

// Chart configuration helpers - Extract configuration to reduce complexity
const INDICATOR_CONFIG = {
  // Main plot indicators
  mainPlot: ['SMA', 'EMA'],
  
  // Subplot assignments
  subplots: {
    y2: ['RSI', 'STOCH_K', 'STOCH_D', 'ADX', 'RSI7'], // Oscillators (0-100)
    y3: ['MACD', 'MACD_Signal', 'MACD_HF', 'MACD_HF_Signal'], // MACD group
    y4: ['BB_High', 'BB_Mid', 'BB_Low', 'BB_Tight_High', 'BB_Tight_Mid', 'BB_Tight_Low', 
         'BB_Wide_High', 'BB_Wide_Mid', 'BB_Wide_Low', 'Ichimoku_Tenkan', 'Ichimoku_Kijun', 
         'Ichimoku_SpanA', 'Ichimoku_SpanB', 'Ichimoku_Chikou', 'SAR'], // Bands & overlays
    y5: ['OBV', 'OBV_MA'] // Volume-based indicators
  },
  
  // Styling configurations
  styling: {
    BB_High: { line: { color: 'rgba(0, 0, 255, 0.5)', width: 1 } },
    BB_Mid: { line: { color: 'rgba(0, 0, 255, 0.5)', dash: 'dash', width: 1 } },
    BB_Low: { 
      line: { color: 'rgba(0, 0, 255, 0.5)', width: 1 },
      fill: 'tonexty',
      fillcolor: 'rgba(0, 0, 255, 0.1)'
    },
    BB_Tight_High: { line: { color: 'rgba(0, 0, 255, 0.5)', width: 1 } },
    BB_Tight_Mid: { line: { color: 'rgba(0, 0, 255, 0.5)', dash: 'dash', width: 1 } },
    BB_Tight_Low: { line: { color: 'rgba(0, 0, 255, 0.5)', width: 1 } },
    BB_Wide_High: { line: { color: 'rgba(0, 0, 128, 0.5)', width: 1 } },
    BB_Wide_Mid: { line: { color: 'rgba(0, 0, 128, 0.5)', dash: 'dash', width: 1 } },
    BB_Wide_Low: { line: { color: 'rgba(0, 0, 128, 0.5)', width: 1 } },
    Ichimoku_SpanA: { line: { color: 'rgba(0, 128, 0, 0.5)', width: 1 } },
    Ichimoku_SpanB: { line: { color: 'rgba(255, 0, 0, 0.3)', width: 1 } },
    Ichimoku_Tenkan: { line: { color: 'blue', width: 1 } },
    Ichimoku_Kijun: { line: { color: 'red', width: 1 } },
    Ichimoku_Chikou: { line: { color: 'green', width: 1 } },
    SAR: { 
      mode: 'markers',
      line: { color: 'purple' },
      marker: { size: 3 }
    }
  },
  
  // Special indicator types
  histogramTypes: ['Histogram', 'MACD_Histogram', 'MACD_HF_Histogram']
};

// Helper to determine subplot for an indicator
const getIndicatorSubplot = (key) => {
  // Check if it belongs on main plot
  if (INDICATOR_CONFIG.mainPlot.some(prefix => key.startsWith(prefix))) {
    return 'y1';
  }
  
  // Check subplots
  for (const [axis, indicators] of Object.entries(INDICATOR_CONFIG.subplots)) {
    if (indicators.includes(key) || indicators.some(ind => key.startsWith(ind))) {
      return axis;
    }
  }
  
  // Default if no match
  return null;
}

// Helper to style an indicator
const getIndicatorStyle = (key, values) => {
  // Default styling
  let style = {
    type: 'scatter',
    mode: 'lines',
    line: { width: 1 },
  };
  
  // Check if it's a histogram
  const isHistogram = INDICATOR_CONFIG.histogramTypes.some(type => key.includes(type));
  if (isHistogram) {
    style.type = 'bar';
    style.mode = undefined;
    // Color bars based on value
    const colors = values.map(v => v >= 0 ? 'rgba(0, 128, 0, 0.5)' : 'rgba(255, 0, 0, 0.5)');
    style.marker = { color: colors };
  }
  
  // Apply specific styling from config if available
  if (INDICATOR_CONFIG.styling[key]) {
    style = { ...style, ...INDICATOR_CONFIG.styling[key] };
  }
  
  return style;
}

// Break down preparePlotData into smaller functions
const createPriceTrace = (chartData, symbol) => {
  const dates = chartData.map(d => d.Date);
  const opens = chartData.map(d => d.Open);
  const highs = chartData.map(d => d.High);
  const lows = chartData.map(d => d.Low);
  const closes = chartData.map(d => d.Close);

  // Candlestick if OHLC data exists
  if (opens.some(isNumeric) && highs.some(isNumeric) && 
      lows.some(isNumeric) && closes.some(isNumeric)) {
    return [{
      x: dates,
      open: opens,
      high: highs,
      low: lows,
      close: closes,
      type: 'candlestick',
      name: symbol || 'Price',
      xaxis: 'x',
      yaxis: 'y1',
      increasing: { line: { color: 'green' } },
      decreasing: { line: { color: 'red' } },
    }];
  } 
  // Fallback to line chart if only Close exists
  else if (closes.some(isNumeric)) {
    return [{
      x: dates,
      y: closes,
      type: 'scatter',
      mode: 'lines',
      name: symbol || 'Close Price',
      yaxis: 'y1',
      line: { color: 'black' }
    }];
  }
  
  return []; // No price data
}

const createIndicatorTraces = (chartData) => {
  if (!chartData || chartData.length === 0) return [];
  
  const dates = chartData.map(d => d.Date);
  const traces = [];
  
  // Find all indicator keys (non-OHLC)
  const indicatorKeys = Object.keys(chartData[0] || {}).filter(
    key => !['Date', 'Open', 'High', 'Low', 'Close', 'Volume'].includes(key) && 
           chartData.some(d => isNumeric(d[key]))
  );
  
  // Create a trace for each indicator
  indicatorKeys.forEach(key => {
    const values = chartData.map(d => d[key]);
    const subplot = getIndicatorSubplot(key);
    
    if (subplot) {
      const style = getIndicatorStyle(key, values);
      
      traces.push({
        x: dates,
        y: values,
        name: key,
        yaxis: subplot,
        ...style
      });
    }
  });
  
  return traces;
}

// Replace the large preparePlotData function
const preparePlotData = (chartData, symbol) => {
  if (!chartData || chartData.length === 0) return [];
  
  const priceTraces = createPriceTrace(chartData, symbol);
  const indicatorTraces = createIndicatorTraces(chartData);
  
  return [...priceTraces, ...indicatorTraces];
};

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

      try {
        const data = await ApiService.getChartData(symbol, selectedParameterSet, period);
        if (data && data.data) {
          setChartData(data.data);
        } else {
          setChartData([]);
        }
      } catch (error) {
        console.error(`Error fetching chart data for ${symbol}:`, error);
        setError(`${t('error_fetching_chart_data')}: ${error.message}`);
      }

    } catch (error) {
      console.error(`Error in chart data process:`, error);
      setError(`${t('error_processing_chart_data')}: ${error.message}`);
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

  const preparePlotLayout = () => {
    // Basic layout, adjust domain for subplots
    const layout = {
      title: `${symbol} - ${t(`parameter_sets.${selectedParameterSet}`)} (${period})`,
      // Remove fixed height to allow responsive sizing
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
      margin: { l: 50, r: 50, t: 80, b: 50 }
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

    const plotData = preparePlotData(chartData, symbol);
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

      <Card className="chart-display" style={{ height: 'calc(80vh - 180px)', minHeight: '500px' }}>
        {renderContent()}
      </Card>
    </div>
  );
};

export default ChartAnalysis;
