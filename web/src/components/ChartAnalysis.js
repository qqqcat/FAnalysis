import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, Row, Col, Typography, Select, Button, Spin, Empty, Alert } from 'antd';
import Plot from 'react-plotly.js';
import ApiService from '../services/ApiService';

const { Title } = Typography;
const { Option } = Select;

// Helper to check if a value is numeric
const isNumeric = (value) => value !== null && value !== undefined && !isNaN(parseFloat(value)) && isFinite(value);

// Helper configuration for which indicators to display by default
const DEFAULT_VISIBLE_INDICATORS = {
  // 主图默认只显示部分关键移动平均线
  mainPlot: ['SMA20', 'SMA50', 'SMA200', 'EMA20'],
  
  // 默认显示的震荡指标
  oscillators: ['RSI', 'STOCH_K', 'STOCH_D'],
  
  // 默认显示的MACD组件
  macd: ['MACD', 'MACD_Signal', 'MACD_Histogram'],
  
  // 默认显示的布林带
  bollinger: ['BB_High', 'BB_Mid', 'BB_Low'],
  
  // 默认显示的成交量指标
  volume: ['OBV', 'OBV_MA'],
  
  // 默认不显示的指标
  hidden: [
    'SMA5', 'SMA9', 'SMA10', 'SMA21', 'SMA100', 'SMA150', 
    'EMA5', 'EMA9', 'EMA10', 'EMA12', 'EMA26', 'EMA50', 'EMA100', 'EMA150', 'EMA200',
    'BB_Tight_High', 'BB_Tight_Mid', 'BB_Tight_Low',
    'BB_Wide_High', 'BB_Wide_Mid', 'BB_Wide_Low',
    'RSI7', 'MACD_HF', 'MACD_HF_Signal', 'MACD_HF_Histogram',
    'Keltner_High', 'Keltner_Mid', 'Keltner_Low'
  ]
};

// Chart configuration helpers
const INDICATOR_CONFIG = {
  // 主图指标
  mainPlot: ['SMA', 'EMA'],
  
  // 子图分配
  subplots: {
    y2: ['RSI', 'STOCH_K', 'STOCH_D', 'ADX', 'RSI7', 'PDI', 'NDI'], // 震荡指标 (0-100)
    y3: ['MACD', 'MACD_Signal', 'MACD_Histogram', 'MACD_HF', 'MACD_HF_Signal', 'MACD_HF_Histogram'], // MACD组
    y4: ['BB_High', 'BB_Mid', 'BB_Low', 'BB_Tight_High', 'BB_Tight_Mid', 'BB_Tight_Low', 
         'BB_Wide_High', 'BB_Wide_Mid', 'BB_Wide_Low', 'Ichimoku_Tenkan', 'Ichimoku_Kijun', 
         'Ichimoku_SpanA', 'Ichimoku_SpanB', 'Ichimoku_Chikou', 'SAR', 'ATR', 'ATR_Percent'], // 带状和叠加指标
    y5: ['OBV', 'OBV_MA'] // 基于成交量的指标
  },
  
  // 样式配置
  styling: {
    // 布林带
    BB_High: { 
      line: { color: 'rgba(65, 105, 225, 0.9)', width: 2 },
      name: '布林上轨',
      visible: true
    },
    BB_Mid: { 
      line: { color: 'rgba(65, 105, 225, 0.9)', dash: 'dash', width: 2 },
      name: '布林中轨',
      visible: true
    },
    BB_Low: { 
      line: { color: 'rgba(65, 105, 225, 0.9)', width: 2 },
      fill: 'tonexty',
      fillcolor: 'rgba(65, 105, 225, 0.15)',
      name: '布林下轨',
      visible: true
    },
    BB_Tight_High: { 
      line: { color: 'rgba(30, 144, 255, 0.8)', width: 1.5 },
      name: '紧布林上轨',
      visible: false
    },
    BB_Tight_Mid: { 
      line: { color: 'rgba(30, 144, 255, 0.8)', dash: 'dash', width: 1.5 },
      name: '紧布林中轨',
      visible: false
    },
    BB_Tight_Low: { 
      line: { color: 'rgba(30, 144, 255, 0.8)', width: 1.5 },
      fill: 'tonexty',
      fillcolor: 'rgba(30, 144, 255, 0.1)',
      name: '紧布林下轨',
      visible: false
    },
    BB_Wide_High: { 
      line: { color: 'rgba(25, 25, 112, 0.8)', width: 1.5 },
      name: '宽布林上轨',
      visible: false
    },
    BB_Wide_Mid: { 
      line: { color: 'rgba(25, 25, 112, 0.8)', dash: 'dash', width: 1.5 },
      name: '宽布林中轨',
      visible: false
    },
    BB_Wide_Low: { 
      line: { color: 'rgba(25, 25, 112, 0.8)', width: 1.5 },
      fill: 'tonexty',
      fillcolor: 'rgba(25, 25, 112, 0.1)',
      name: '宽布林下轨',
      visible: false
    },
    
    // Ichimoku
    Ichimoku_SpanA: { 
      line: { color: 'rgba(0, 128, 0, 0.7)', width: 2 },
      name: '转折线A',
      visible: false
    },
    Ichimoku_SpanB: { 
      line: { color: 'rgba(220, 20, 60, 0.7)', width: 2 },
      fill: 'tonexty',
      fillcolor: 'rgba(200, 200, 200, 0.3)',
      name: '转折线B',
      visible: false
    },
    Ichimoku_Tenkan: { 
      line: { color: 'rgba(0, 0, 255, 0.8)', width: 2 }, 
      name: '转换线',
      visible: false
    },
    Ichimoku_Kijun: { 
      line: { color: 'rgba(255, 0, 0, 0.8)', width: 2 }, 
      name: '基准线',
      visible: false
    },
    Ichimoku_Chikou: { 
      line: { color: 'rgba(0, 128, 0, 0.8)', width: 2 }, 
      name: '迟行线',
      visible: false
    },
    
    // 其他指标
    SAR: { 
      mode: 'markers',
      marker: { size: 4, color: 'rgba(128, 0, 128, 0.8)' },
      name: 'SAR',
      visible: false
    },
    
    // 移动平均线颜色
    SMA5: { 
      line: { color: 'rgba(30, 144, 255, 0.9)', width: 2 }, 
      name: 'SMA5',
      visible: false
    },
    SMA10: { 
      line: { color: 'rgba(220, 20, 60, 0.9)', width: 2 }, 
      name: 'SMA10',
      visible: false
    },
    SMA20: { 
      line: { color: 'rgba(50, 205, 50, 1)', width: 2.5 }, 
      name: 'SMA20',
      visible: true
    },
    SMA50: { 
      line: { color: 'rgba(148, 0, 211, 1)', width: 2.5 }, 
      name: 'SMA50',
      visible: true
    },
    SMA100: { 
      line: { color: 'rgba(255, 140, 0, 0.9)', width: 2 }, 
      name: 'SMA100',
      visible: false
    },
    SMA200: { 
      line: { color: 'rgba(0, 0, 0, 1)', width: 3 }, 
      name: 'SMA200',
      visible: true
    },
    
    EMA5: { 
      line: { color: 'rgba(30, 144, 255, 0.9)', width: 2, dash: 'dot' }, 
      name: 'EMA5',
      visible: false
    },
    EMA10: { 
      line: { color: 'rgba(220, 20, 60, 0.9)', width: 2, dash: 'dot' }, 
      name: 'EMA10',
      visible: false
    },
    EMA20: { 
      line: { color: 'rgba(50, 205, 50, 1)', width: 2.5, dash: 'dot' }, 
      name: 'EMA20',
      visible: true
    },
    EMA50: { 
      line: { color: 'rgba(148, 0, 211, 0.9)', width: 2, dash: 'dot' }, 
      name: 'EMA50',
      visible: false
    },
    EMA100: { 
      line: { color: 'rgba(255, 140, 0, 0.9)', width: 2, dash: 'dot' }, 
      name: 'EMA100',
      visible: false
    },
    EMA200: { 
      line: { color: 'rgba(0, 0, 0, 0.9)', width: 2.5, dash: 'dot' }, 
      name: 'EMA200',
      visible: false 
    },
    
    // PDI和NDI
    PDI: { 
      line: { color: 'rgba(0, 128, 0, 0.9)', width: 2 }, 
      name: 'PDI',
      visible: false
    },
    NDI: { 
      line: { color: 'rgba(220, 20, 60, 0.9)', width: 2 }, 
      name: 'NDI',
      visible: false
    },
    ADX: { 
      line: { color: 'rgba(128, 128, 128, 1)', width: 2 }, 
      name: 'ADX',
      visible: false
    },
    
    // 震荡指标
    RSI: { 
      line: { color: 'rgba(34, 139, 34, 1)', width: 2.5 }, 
      name: 'RSI',
      visible: true
    },
    RSI7: { 
      line: { color: 'rgba(139, 0, 0, 0.9)', width: 2 }, 
      name: 'RSI7',
      visible: false
    },
    STOCH_K: { 
      line: { color: 'rgba(65, 105, 225, 1)', width: 2 }, 
      name: 'STOCH_K',
      visible: true
    },
    STOCH_D: { 
      line: { color: 'rgba(220, 20, 60, 1)', width: 2 }, 
      name: 'STOCH_D',
      visible: true
    },
    
    // MACD
    MACD: { 
      line: { color: 'rgba(65, 105, 225, 1)', width: 2.5 }, 
      name: 'MACD',
      visible: true 
    },
    MACD_Signal: { 
      line: { color: 'rgba(220, 20, 60, 1)', width: 2.5 }, 
      name: 'MACD信号',
      visible: true
    },
    MACD_Histogram: { 
      type: 'bar',
      marker: { color: [] },  // 将在创建轨迹时动态填充
      name: 'MACD柱状',
      visible: true
    },
    MACD_HF: { 
      line: { color: 'rgba(70, 130, 180, 0.8)', width: 2 }, 
      name: 'MACD_HF',
      visible: false
    },
    MACD_HF_Signal: { 
      line: { color: 'rgba(205, 92, 92, 0.8)', width: 2 }, 
      name: 'MACD_HF信号',
      visible: false
    },
    MACD_HF_Histogram: { 
      type: 'bar',
      marker: { color: [] },  // 将在创建轨迹时动态填充
      name: 'MACD_HF柱状',
      visible: false
    },
    
    // 成交量
    OBV: { 
      line: { color: 'rgba(70, 130, 180, 1)', width: 2.5 }, 
      name: 'OBV',
      visible: true 
    },
    OBV_MA: { 
      line: { color: 'rgba(205, 92, 92, 1)', width: 2.5, dash: 'dash' }, 
      name: 'OBV均线',
      visible: true
    }
  },
  
  // 特殊指标类型
  histogramTypes: ['Histogram', 'MACD_Histogram', 'MACD_HF_Histogram'],
};

// Helper to determine subplot for an indicator
const getIndicatorSubplot = (key) => {
  // 检查是否属于主图
  if (INDICATOR_CONFIG.mainPlot.some(prefix => key.startsWith(prefix))) {
    return 'y';
  }
  
  // 检查子图
  for (const [axis, indicators] of Object.entries(INDICATOR_CONFIG.subplots)) {
    if (indicators.some(ind => key === ind || key.startsWith(ind + '_') || ind.endsWith(key))) {
      return axis;
    }
  }
  
  // 默认情况
  return null;
};

// Helper to style an indicator
const getIndicatorStyle = (key, values) => {
  // 默认样式
  let style = {
    type: 'scatter',
    mode: 'lines',
    line: { width: 1 },
    visible: !DEFAULT_VISIBLE_INDICATORS.hidden.includes(key)
  };
  
  // 为特定指标组设置默认可见性
  if (DEFAULT_VISIBLE_INDICATORS.mainPlot.includes(key)) {
    style.visible = true;
  } else if (DEFAULT_VISIBLE_INDICATORS.oscillators.includes(key)) {
    style.visible = true;
  } else if (DEFAULT_VISIBLE_INDICATORS.macd.includes(key)) {
    style.visible = true;
  } else if (DEFAULT_VISIBLE_INDICATORS.bollinger.includes(key)) {
    style.visible = true;
  } else if (DEFAULT_VISIBLE_INDICATORS.volume.includes(key)) {
    style.visible = true;
  }
  
  // 检查是否为柱状图
  const isHistogram = INDICATOR_CONFIG.histogramTypes.some(type => key.includes(type));
  if (isHistogram) {
    style.type = 'bar';
    style.mode = undefined;
    // 基于值给柱状图上色
    const colors = values.map(v => v >= 0 ? 'rgba(0, 128, 0, 0.7)' : 'rgba(255, 0, 0, 0.7)');
    style.marker = { color: colors };
  }
  
  // 应用配置中的特定样式（如果有）
  if (INDICATOR_CONFIG.styling[key]) {
    style = { ...style, ...INDICATOR_CONFIG.styling[key] };
  }
  
  return style;
};

// 创建价格轨迹
const createPriceTrace = (data, symbol) => {
  if (!data || data.length === 0) {
    console.warn('No data for price trace');
    return [];
  }
  
  const dates = data.map(d => d.Date);
  const opens = data.map(d => d.Open);
  const highs = data.map(d => d.High);
  const lows = data.map(d => d.Low);
  const closes = data.map(d => d.Close);
  
  // 验证是否有足够的OHLC数据
  const hasOHLC = opens.some(isNumeric) && 
                 highs.some(isNumeric) && 
                 lows.some(isNumeric) && 
                 closes.some(isNumeric);
  
  if (hasOHLC) {
    console.log('Creating candlestick chart');
    return [{
      x: dates,
      open: opens,
      high: highs,
      low: lows,
      close: closes,
      type: 'candlestick',
      name: symbol || '价格',
      yaxis: 'y',
      increasing: { line: { color: '#26a69a', width: 1 } },
      decreasing: { line: { color: '#ef5350', width: 1 } },
      showlegend: true,
      legendgroup: 'price',
      visible: true
    }];
  } else if (closes.some(isNumeric)) {
    console.log('Falling back to line chart for price');
    return [{
      x: dates,
      y: closes.map(v => isNumeric(v) ? v : null),
      type: 'scatter',
      mode: 'lines',
      name: `${symbol || ''} 收盘价`,
      yaxis: 'y',
      line: { color: 'rgba(0,0,0,0.7)', width: 2 },
      showlegend: true,
      legendgroup: 'price',
      visible: true
    }];
  }
  
  console.warn('No valid price data');
  return [];
};

// 创建移动平均线轨迹
const createMATraces = (data) => {
  if (!data || data.length === 0) return [];
  
  const dates = data.map(d => d.Date);
  const traces = [];
  const maIndicators = [
    'SMA5', 'SMA10', 'SMA20', 'SMA50', 'SMA100', 'SMA200',
    'EMA5', 'EMA10', 'EMA20', 'EMA50', 'EMA100', 'EMA200'
  ];
  
  // 为每个MA创建轨迹
  maIndicators.forEach(key => {
    const values = data.map(d => d[key]);
    if (!values.some(isNumeric)) return;
    
    const cleanValues = values.map(v => isNumeric(v) ? v : null);
    const style = getIndicatorStyle(key, cleanValues);
    
    traces.push({
      x: dates,
      y: cleanValues,
      name: style.name || key,
      yaxis: 'y',
      showlegend: true,
      legendgroup: 'ma',
      ...style
    });
  });
  
  return traces;
};

// 创建震荡指标轨迹 (RSI, Stoch, ADX)  
const createOscillatorTraces = (data) => {
  if (!data || data.length === 0) return [];
  
  const dates = data.map(d => d.Date);
  const traces = [];
  const indicators = ['RSI', 'RSI7', 'STOCH_K', 'STOCH_D', 'ADX', 'PDI', 'NDI'];
  
  indicators.forEach(key => {
    const values = data.map(d => d[key]);
    if (!values.some(isNumeric)) return;
    
    const cleanValues = values.map(v => isNumeric(v) ? v : null);
    const style = getIndicatorStyle(key, cleanValues);
    
    traces.push({
      x: dates,
      y: cleanValues,
      name: style.name || key,
      yaxis: 'y2',
      showlegend: true,
      legendgroup: 'oscillators',
      ...style
    });
  });
  
  return traces;
};

// 创建MACD轨迹
const createMACDTraces = (data) => {
  if (!data || data.length === 0) return [];
  
  const dates = data.map(d => d.Date);
  const traces = [];
  const indicators = [
    'MACD', 'MACD_Signal', 'MACD_Histogram',
    'MACD_HF', 'MACD_HF_Signal', 'MACD_HF_Histogram'
  ];
  
  indicators.forEach(key => {
    const values = data.map(d => d[key]);
    if (!values.some(isNumeric)) return;
    
    const cleanValues = values.map(v => isNumeric(v) ? v : null);
    const style = getIndicatorStyle(key, cleanValues);
    
    // 如果是柱状图，动态设置颜色
    if (key.includes('Histogram')) {
      const colors = cleanValues.map(v => 
        isNumeric(v) ? (v >= 0 ? 'rgba(0, 128, 0, 0.7)' : 'rgba(255, 0, 0, 0.7)') : 'rgba(0,0,0,0)'
      );
      if (!style.marker) style.marker = {};
      style.marker.color = colors;
    }
    
    traces.push({
      x: dates,
      y: cleanValues,
      name: style.name || key,
      yaxis: 'y3',
      showlegend: true,
      legendgroup: 'macd',
      ...style
    });
  });
  
  return traces;
};

// 创建波动率相关指标轨迹 (布林带, ATR)
const createVolatilityTraces = (data) => {
  if (!data || data.length === 0) return [];
  
  const dates = data.map(d => d.Date);
  const traces = [];
  
  // 布林带
  const bbGroups = [
    ['BB_High', 'BB_Mid', 'BB_Low'],
    ['BB_Tight_High', 'BB_Tight_Mid', 'BB_Tight_Low'],
    ['BB_Wide_High', 'BB_Wide_Mid', 'BB_Wide_Low']
  ];
  
  bbGroups.forEach(group => {
    // 检查这组布林带是否有足够数据
    const hasData = group.some(key => 
      data.some(d => isNumeric(d[key]))
    );
    
    if (!hasData) return;
    
    // 创建布林带轨迹，顺序很重要，必须先创建下轨，再创建中轨和上轨
    // 以保证填充区域正确
    const orderedGroup = [group[2], group[1], group[0]]; // Low, Mid, High
    
    orderedGroup.forEach(key => {
      const values = data.map(d => d[key]);
      if (!values.some(isNumeric)) return;
      
      const cleanValues = values.map(v => isNumeric(v) ? v : null);
      const style = getIndicatorStyle(key, cleanValues);
      
      traces.push({
        x: dates,
        y: cleanValues,
        name: style.name || key,
        yaxis: 'y4',
        showlegend: true,
        legendgroup: 'volatility',
        ...style
      });
    });
  });
  
  // Ichimoku - 遵循特定绘制顺序以确保正确填充
  const ichimokuOrder = [
    'Ichimoku_SpanB', 'Ichimoku_SpanA', // 先绘制云区
    'Ichimoku_Tenkan', 'Ichimoku_Kijun', 'Ichimoku_Chikou' // 再绘制线
  ];
  
  // 检查是否有足够的Ichimoku数据
  const hasIchimoku = ichimokuOrder.some(key => 
    data.some(d => isNumeric(d[key]))
  );
  
  if (hasIchimoku) {
    ichimokuOrder.forEach(key => {
      const values = data.map(d => d[key]);
      if (!values.some(isNumeric)) return;
      
      const cleanValues = values.map(v => isNumeric(v) ? v : null);
      const style = getIndicatorStyle(key, cleanValues);
      
      traces.push({
        x: dates,
        y: cleanValues,
        name: style.name || key,
        yaxis: 'y4',
        showlegend: true,
        legendgroup: 'ichimoku',
        ...style
      });
    });
  }
  
  // SAR
  const sarValues = data.map(d => d.SAR);
  if (sarValues.some(isNumeric)) {
    const cleanValues = sarValues.map(v => isNumeric(v) ? v : null);
    const style = getIndicatorStyle('SAR', cleanValues);
    
    traces.push({
      x: dates,
      y: cleanValues,
      name: style.name || 'SAR',
      yaxis: 'y4',
      showlegend: true,
      legendgroup: 'volatility',
      ...style
    });
  }
  
  return traces;
};

// 创建基于成交量的指标轨迹
const createVolumeTraces = (data) => {
  if (!data || data.length === 0) return [];
  
  const dates = data.map(d => d.Date);
  const traces = [];
  const indicators = ['OBV', 'OBV_MA'];
  
  indicators.forEach(key => {
    const values = data.map(d => d[key]);
    if (!values.some(isNumeric)) return;
    
    const cleanValues = values.map(v => isNumeric(v) ? v : null);
    const style = getIndicatorStyle(key, cleanValues);
    
    traces.push({
      x: dates,
      y: cleanValues,
      name: style.name || key,
      yaxis: 'y5',
      showlegend: true,
      legendgroup: 'volume',
      ...style
    });
  });
  
  return traces;
};

const ChartAnalysis = () => {
  const { symbol } = useParams();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [parametersLoading, setParametersLoading] = useState(false);
  const [parameterSets, setParameterSets] = useState([]);
  const [selectedParameterSet, setSelectedParameterSet] = useState('default');
  const [period, setPeriod] = useState('1y');
  const [chartData, setChartData] = useState([]); 
  const [error, setError] = useState(null);

  // 加载可用参数集
  useEffect(() => {
    const fetchParameters = async () => {
      try {
        setParametersLoading(true);
        const data = await ApiService.getParameters();
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

  // 获取图表数据函数
  const fetchChartData = useCallback(async () => {
    if (!symbol) return;
    try {
      setLoading(true);
      setError(null);
      setChartData([]); // 清除先前数据

      try {
        console.log(`Fetching chart data for ${symbol} with parameter set ${selectedParameterSet} and period ${period}`);
        const data = await ApiService.getChartData(symbol, selectedParameterSet, period);
        if (data && data.data) {
          console.log(`Received ${data.data.length} data points`);
          setChartData(data.data);
        } else {
          console.warn('No data received');
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

  // 当symbol, parameter set, 或 period改变时获取数据
  useEffect(() => {
    fetchChartData();
  }, [fetchChartData]);

  const handleParameterChange = (value) => {
    setSelectedParameterSet(value);
  };

  const handlePeriodChange = (value) => {
    setPeriod(value);
  };

  // 准备所有图表数据
  const preparePlotData = () => {
    if (!chartData || chartData.length === 0) {
      console.warn('No chart data available');
      return [];
    }
    
    console.log(`Preparing plot data with ${chartData.length} points`);
    
    // 收集所有轨迹
    const priceTraces = createPriceTrace(chartData, symbol);
    const maTraces = createMATraces(chartData);
    const oscillatorTraces = createOscillatorTraces(chartData);
    const macdTraces = createMACDTraces(chartData);
    const volatilityTraces = createVolatilityTraces(chartData);
    const volumeTraces = createVolumeTraces(chartData);
    
    // 组合所有轨迹
    const allTraces = [
      ...priceTraces,
      ...maTraces,
      ...oscillatorTraces,
      ...macdTraces,
      ...volatilityTraces,
      ...volumeTraces
    ];
    
    console.log(`Created ${allTraces.length} traces total`);
    return allTraces;
  };

  const preparePlotLayout = () => {
    // 基本布局
    const layout = {
      autosize: true,
      title: {
        text: `${symbol} - ${t(`parameter_sets.${selectedParameterSet}`, selectedParameterSet)} (${period})`,
        font: { size: 20, color: '#333' }
      },
      paper_bgcolor: 'rgba(255,255,255,0.95)',
      plot_bgcolor: 'rgba(250,250,250,0.95)',
      dragmode: 'zoom',
      showlegend: true,
      legend: { 
        orientation: "h", 
        y: 1.12,
        x: 0.5,
        xanchor: 'center',
        font: { size: 10, color: '#333' },
        bgcolor: 'rgba(255,255,255,0.9)',
        bordercolor: 'rgba(200,200,200,0.5)',
        borderwidth: 1,
        groupclick: 'legendonly',
        tracegroupgap: 8
      },
      margin: { l: 50, r: 60, t: 60, b: 30, pad: 5 },
      
      // 确保所有子图都使用相同的X轴范围
      xaxis: { 
        domain: [0, 1],
        rangeslider: { visible: false },
        type: 'date',
        tickformat: '%Y-%m-%d',
        showticklabels: true,
        showgrid: true,
        gridcolor: 'rgba(200, 200, 200, 0.3)',
        zeroline: false,
        linecolor: 'rgba(150, 150, 150, 0.5)',
        tickfont: { size: 10 }
      },
      
      // 主图 - 价格和MA
      yaxis: {
        domain: [0.68, 1],
        title: {
          text: 'Price',
          font: { size: 12 }
        },
        autorange: true,
        showgrid: true,
        gridcolor: 'rgba(200, 200, 200, 0.3)',
        zeroline: false,
        fixedrange: false,
        side: 'right',
        tickfont: { size: 10 }
      },
      
      // 子图1 - 震荡指标
      yaxis2: {
        domain: [0.48, 0.66],
        title: {
          text: 'Oscillators',
          font: { size: 12 }
        },
        fixedrange: false,
        autorange: true,
        showgrid: true,
        gridcolor: 'rgba(200, 200, 200, 0.3)',
        side: 'right',
        range: [0, 100], // 固定RSI和随机指标的范围
        tickfont: { size: 10 }
      },
      
      // 子图2 - MACD
      yaxis3: {
        domain: [0.28, 0.46],
        title: {
          text: 'MACD',
          font: { size: 12 }
        },
        fixedrange: false,
        autorange: true,
        showgrid: true,
        gridcolor: 'rgba(200, 200, 200, 0.3)',
        zeroline: true,
        zerolinecolor: 'rgba(120, 120, 120, 0.5)',
        side: 'right',
        tickfont: { size: 10 }
      },
      
      // 子图3 - 波动率指标
      yaxis4: {
        domain: [0.08, 0.26],
        title: {
          text: 'Volatility',
          font: { size: 12 }
        },
        fixedrange: false,
        autorange: true,
        showgrid: true,
        gridcolor: 'rgba(200, 200, 200, 0.3)',
        side: 'right',
        tickfont: { size: 10 }
      },
      
      // 子图4 - 成交量
      yaxis5: {
        domain: [0, 0.06],
        title: {
          text: 'Volume',
          font: { size: 10 }
        },
        fixedrange: false,
        autorange: true,
        showgrid: true,
        gridcolor: 'rgba(200, 200, 200, 0.3)',
        side: 'right',
        tickfont: { size: 9 }
      },
      
      grid: {
        rows: 5,
        columns: 1,
        pattern: 'independent',
        roworder: 'top to bottom'
      },
      
      hovermode: 'x unified',
      hoverlabel: {
        bgcolor: 'rgba(255, 255, 255, 0.9)',
        bordercolor: '#888',
        font: { size: 12, color: '#333' },
        namelength: 30
      },
      modebar: {
        bgcolor: 'rgba(255, 255, 255, 0.9)',
        color: '#333',
        activecolor: '#2196F3'
      }
    };

    // 为RSI添加水平参考线
    layout.shapes = [
      // RSI参考线
      { type: 'line', xref: 'paper', x0: 0, x1: 1, yref: 'y2', y0: 70, y1: 70, 
        line: { color: 'rgba(255, 0, 0, 0.6)', width: 1, dash: 'dash' } },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, yref: 'y2', y0: 30, y1: 30, 
        line: { color: 'rgba(0, 128, 0, 0.6)', width: 1, dash: 'dash' } },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, yref: 'y2', y0: 50, y1: 50, 
        line: { color: 'rgba(120, 120, 120, 0.4)', width: 1, dash: 'dot' } },
      
      // MACD零线
      { type: 'line', xref: 'paper', x0: 0, x1: 1, yref: 'y3', y0: 0, y1: 0, 
        line: { color: 'rgba(120, 120, 120, 0.5)', width: 1, dash: 'dot' } }
    ];

    return layout;
  };

  // 渲染内容
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
        config={{ 
          responsive: true,
          scrollZoom: true,
          displayModeBar: true,
          modeBarButtonsToAdd: ['drawline', 'drawopenpath', 'eraseshape'],
          modeBarButtonsToRemove: ['lasso2d', 'select2d'],
          toImageButtonOptions: {
            filename: `${symbol}_${selectedParameterSet}_${period}`,
            scale: 2
          }
        }}
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
            <Button
              type="primary"
              onClick={fetchChartData}
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

      <Card className="chart-display" style={{ height: 'calc(85vh - 180px)', minHeight: '600px' }}>
        {renderContent()}
      </Card>
    </div>
  );
};

export default ChartAnalysis;
