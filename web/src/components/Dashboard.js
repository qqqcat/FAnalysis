import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, Row, Col, Typography, Select, Button, Spin, Table, Alert, Tag } from 'antd';
import { useNavigate } from 'react-router-dom';
import ApiService from '../services/ApiService';

const { Title, Text } = Typography;
const { Option } = Select;

// Custom hooks for data fetching
const useAssetCategories = () => {
  const { t } = useTranslation();
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const categories = await ApiService.getAssets();
      setData(categories);
    } catch (err) {
      console.error('Error fetching asset categories:', err);
      setError(t('dashboard.errors.categories_fetch_error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
};

const useMarketSummary = () => {
  const { t } = useTranslation();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const marketSummaryData = await ApiService.getMarketSummary();
      setData(marketSummaryData);
    } catch (err) {
      console.error('Error fetching market summary:', err);
      setError(t('dashboard.errors.market_summary_error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
};

const useOptimalIndicators = (category) => {
  const { t } = useTranslation();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    if (!category) return;

    try {
      setLoading(true);
      setError(null);
      const indicators = await ApiService.getOptimalIndicators(category);
      setData(indicators);
    } catch (err) {
      console.error(`Error fetching optimal indicators for ${category}:`, err);
      setError(t('dashboard.errors.indicators_fetch_error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [category]);

  return { data, loading, error, refetch: fetchData };
};

const useRecentReports = () => {
  const { t } = useTranslation();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const reports = await ApiService.getRecentReports();
      setData(reports);
    } catch (err) {
      console.error('Error fetching recent reports:', err);
      setError(t('dashboard.errors.reports_fetch_error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
};

const Dashboard = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const { data: assetCategories, loading: assetLoading, error: assetError, refetch: refetchAssets } = useAssetCategories();
  const { data: marketSummary, loading: marketLoading, error: marketError, refetch: refetchMarket } = useMarketSummary();
  const [selectedCategory, setSelectedCategory] = useState('forex');
  const [selectedAsset, setSelectedAsset] = useState('');

  const {
    data: optimalIndicators,
    loading: indicatorsLoading,
    error: indicatorsError,
    refetch: refetchIndicators,
  } = useOptimalIndicators(selectedCategory);

  const {
    data: recentReports,
    loading: reportsLoading,
    error: reportsError,
    refetch: refetchReports,
  } = useRecentReports();

  useEffect(() => {
    if (assetCategories && Object.keys(assetCategories).length > 0) {
      if (!selectedCategory || !assetCategories[selectedCategory]) {
        const firstCategory = Object.keys(assetCategories)[0];
        setSelectedCategory(firstCategory);
      }

      if (assetCategories[selectedCategory]?.length > 0 && !selectedAsset) {
        setSelectedAsset(assetCategories[selectedCategory][0]);
      }
    }
  }, [assetCategories, selectedCategory, selectedAsset]);

  const handleCategoryChange = (value) => {
    setSelectedCategory(value);

    if (assetCategories[value] && assetCategories[value].length > 0) {
      setSelectedAsset(assetCategories[value][0]);
    } else {
      setSelectedAsset('');
    }
  };

  const handleAssetChange = (value) => {
    setSelectedAsset(value);
  };

  const goToAnalysis = () => {
    if (selectedAsset) {
      navigate(`/analysis/${selectedAsset}`);
    }
  };

  const marketSummaryColumns = [
    {
      title: t('dashboard.asset'),
      dataIndex: 'asset',
      key: 'asset',
    },
    {
      title: t('dashboard.last_price'),
      dataIndex: 'lastPrice',
      key: 'lastPrice',
      render: (price) => price.toFixed(price >= 100 ? 2 : 4),
    },
    {
      title: t('dashboard.change'),
      dataIndex: 'change',
      key: 'change',
      render: (change, record) => (
        <span style={{ color: record.trend === 'up' ? 'green' : 'red' }}>
          {record.trend === 'up' ? '+' : ''}{change.toFixed(change >= 1 ? 2 : 4)}
        </span>
      ),
    },
    {
      title: t('dashboard.change_percent'),
      dataIndex: 'changePercent',
      key: 'changePercent',
      render: (percent, record) => (
        <span style={{ color: record.trend === 'up' ? 'green' : 'red' }}>
          {record.trend === 'up' ? '+' : ''}{percent.toFixed(2)}%
        </span>
      ),
    },
    {
      title: t('dashboard.action'),
      key: 'action',
      render: (_, record) => (
        <Button
          type="link"
          onClick={() => navigate(`/analysis/${record.asset}`)}
        >
          {t('dashboard.view_details')}
        </Button>
      ),
    },
  ];

  const getIndicatorDescription = (indicator) => {
    const descriptions = {
      RSI: t('indicator_descriptions.rsi', 'Relative Strength Index - Measures momentum and overbought/oversold conditions'),
      MACD: t('indicator_descriptions.macd', 'Moving Average Convergence Divergence - Trend-following momentum indicator'),
      BollingerBands: t('indicator_descriptions.bollinger', 'Volatility bands placed above and below a moving average'),
      Stochastic: t('indicator_descriptions.stochastic', 'Compares a closing price to its price range over time'),
      ADX: t('indicator_descriptions.adx', 'Average Directional Index - Measures trend strength'),
      Ichimoku: t('indicator_descriptions.ichimoku', 'Cloud chart showing support, resistance and momentum'),
      EMA: t('indicator_descriptions.ema', 'Exponential Moving Average - Gives more weight to recent prices'),
      SMA: t('indicator_descriptions.sma', 'Simple Moving Average - Average of prices over a specific period'),
    };

    return descriptions[indicator] || indicator;
  };

  const isInitialLoading = assetLoading && Object.keys(assetCategories).length === 0;

  if (isInitialLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>{t('loading')}</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container enhanced-dashboard">
      <Title level={2} className="dashboard-title">Dashboard</Title>
      <div className="dashboard-welcome">
        <Text type="secondary" style={{ fontSize: 18 }}>
          {t('dashboard.welcome', 'Welcome to your financial analysis dashboard!')}
        </Text>
      </div>

      {assetError && (
        <Alert
          message={t('dashboard.errors.title')}
          description={assetError}
          type="error"
          showIcon
          className="mb-4"
          action={
            <Button size="small" onClick={refetchAssets}>
              {t('retry')}
            </Button>
          }
        />
      )}

      <Card className="mb-4 dashboard-card" bordered={false}>
        <Row gutter={16} align="middle">
          <Col xs={24} md={8}>
            <Select
              placeholder={t('chart_analysis.select_symbol')}
              onChange={handleCategoryChange}
              value={selectedCategory}
              style={{ width: '100%', marginBottom: '10px' }}
              loading={assetLoading}
            >
              {Object.keys(assetCategories).map((category) => (
                <Option key={category} value={category}>
                  {t(`categories.${category}`)}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} md={8}>
            <Select
              placeholder={t('chart_analysis.select_symbol')}
              onChange={handleAssetChange}
              value={selectedAsset}
              style={{ width: '100%', marginBottom: '10px' }}
              disabled={!selectedCategory || assetLoading}
              loading={assetLoading}
            >
              {assetCategories[selectedCategory]?.map((asset) => (
                <Option key={asset} value={asset}>{asset}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} md={8}>
            <Button
              type="primary"
              onClick={goToAnalysis}
              disabled={!selectedAsset}
              style={{ width: '100%' }}
            >
              {t('chart_analysis.generate_charts')}
            </Button>
          </Col>
        </Row>
      </Card>

      <Row gutter={16} className="mb-4">
        <Col span={24}>
          <Card
            className="dashboard-card"
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>{t('dashboard.market_summary')}</span>
                {marketLoading && <Spin size="small" />}
              </div>
            }
            bordered={false}
            extra={
              <Button
                size="small"
                onClick={refetchMarket}
                disabled={marketLoading}
              >
                {t('refresh')}
              </Button>
            }
          >
            {marketError ? (
              <Alert
                message={marketError}
                type="error"
                showIcon
                action={
                  <Button size="small" onClick={refetchMarket}>
                    {t('retry')}
                  </Button>
                }
              />
            ) : (
              <Table
                dataSource={marketSummary}
                columns={marketSummaryColumns}
                rowKey="asset"
                pagination={false}
                size="middle"
                loading={marketLoading}
              />
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Card
            className="dashboard-card"
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>{`${t('dashboard.optimal_indicators', 'Optimal Indicators')} - ${t(`categories.${selectedCategory}`)}`}</span>
                {indicatorsLoading && <Spin size="small" />}
              </div>
            }
            bordered={false}
            extra={
              <Button
                size="small"
                onClick={refetchIndicators}
                disabled={indicatorsLoading}
              >
                {t('refresh')}
              </Button>
            }
          >
            {indicatorsError ? (
              <Alert
                message={indicatorsError}
                type="error"
                showIcon
                action={
                  <Button size="small" onClick={refetchIndicators}>
                    {t('retry')}
                  </Button>
                }
              />
            ) : optimalIndicators.length > 0 ? (
              <ul className="indicator-list">
                {optimalIndicators.map((indicator, index) => (
                  <li key={index} className="indicator-item">
                    <div>
                      <Tag color="blue">{indicator}</Tag>
                      <Text type="secondary" style={{ display: 'block', fontSize: '12px', marginTop: '5px' }}>
                        {getIndicatorDescription(indicator)}
                      </Text>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <Alert
                message={t('no_data')}
                type="info"
              />
            )}
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card
            className="dashboard-card"
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>{t('dashboard.recent_reports', 'Recent Reports')}</span>
                {reportsLoading && <Spin size="small" />}
              </div>
            }
            bordered={false}
            extra={
              <Button
                size="small"
                onClick={refetchReports}
                disabled={reportsLoading}
              >
                {t('refresh')}
              </Button>
            }
          >
            {reportsError ? (
              <Alert
                message={reportsError}
                type="error"
                showIcon
                action={
                  <Button size="small" onClick={refetchReports}>
                    {t('retry')}
                  </Button>
                }
              />
            ) : recentReports.length > 0 ? (
              <ul className="report-list">
                {recentReports.map((report, index) => (
                  <li key={index} className="report-item">
                    <a href={report.url}>
                      {report.symbol} - {report.parameterSet}
                    </a>
                    <div className="report-meta">
                      <Text type="secondary">{report.date}</Text>
                      <Button
                        type="link"
                        size="small"
                        onClick={() => navigate(`/reports/${report.filename}`)}
                      >
                        {t('dashboard.view')}
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <Alert
                message={t('no_data')}
                type="info"
                action={
                  <Button
                    size="small"
                    type="primary"
                    onClick={() => navigate('/reports')}
                  >
                    {t('detailed_report.generate_new_report')}
                  </Button>
                }
              />
            )}
          </Card>
        </Col>
      </Row>

      <style jsx="true">{`
        .report-list, .indicator-list {
          padding: 0;
          margin: 0;
          list-style: none;
        }
        .report-item, .indicator-item {
          padding: 10px 0;
          border-bottom: 1px solid #f0f0f0;
        }
        .report-item:last-child, .indicator-item:last-child {
          border-bottom: none;
        }
        .report-meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 5px;
        }
      `}</style>
    </div>
  );
};

export default Dashboard;