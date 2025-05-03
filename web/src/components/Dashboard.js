import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, Row, Col, Typography, Select, Button, Spin, Table, Alert, Divider, Statistic, Tag } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, DashOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import ApiService from '../services/ApiService';

const { Title, Text } = Typography;
const { Option } = Select;

const Dashboard = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [assetCategories, setAssetCategories] = useState({});
  const [selectedCategory, setSelectedCategory] = useState('forex');
  const [selectedAsset, setSelectedAsset] = useState('');
  const [marketSummary, setMarketSummary] = useState([]);
  const [optimalIndicators, setOptimalIndicators] = useState([]);
  const [recentReports, setRecentReports] = useState([]);
  
  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch asset categories
        const categories = await ApiService.getAssets();
        setAssetCategories(categories);
        
        // Set default selected asset from first category
        if (categories && Object.keys(categories).length > 0) {
          const firstCategory = Object.keys(categories)[0];
          setSelectedCategory(firstCategory);
          
          if (categories[firstCategory].length > 0) {
            setSelectedAsset(categories[firstCategory][0]);
          }
        }
        
        // 获取实时市场概览数据，而不是使用硬编码数据
        try {
          const marketSummaryData = await ApiService.getMarketSummary();
          setMarketSummary(marketSummaryData);
        } catch (marketError) {
          console.error('Error fetching market summary:', marketError);
          // 如果API请求失败，使用备用数据
          setMarketSummary([
            { asset: 'EURUSD', lastPrice: 1.0784, change: 0.0023, changePercent: 0.21, trend: 'up' },
            { asset: 'GOLD', lastPrice: 2334.50, change: -12.70, changePercent: -0.54, trend: 'down' },
            { asset: 'S&P500', lastPrice: 5021.84, change: 32.40, changePercent: 0.65, trend: 'up' },
            { asset: 'NASDAQ', lastPrice: 15848.16, change: 124.35, changePercent: 0.79, trend: 'up' },
            { asset: 'OIL', lastPrice: 82.63, change: -1.45, changePercent: -1.72, trend: 'down' }
          ]);
        }
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
    
    // 设置定时器定期刷新市场概览数据（每60秒刷新一次）
    const marketDataInterval = setInterval(async () => {
      try {
        const marketSummaryData = await ApiService.getMarketSummary();
        setMarketSummary(marketSummaryData);
        console.log('Market data refreshed');
      } catch (error) {
        console.error('Error refreshing market data:', error);
      }
    }, 60000);
    
    // 清理定时器
    return () => clearInterval(marketDataInterval);
  }, []);
  
  // Fetch optimal indicators when selected category changes
  useEffect(() => {
    const fetchOptimalIndicators = async () => {
      if (selectedCategory) {
        try {
          const indicators = await ApiService.getOptimalIndicators(selectedCategory);
          setOptimalIndicators(indicators);
        } catch (error) {
          console.error(`Error fetching optimal indicators for ${selectedCategory}:`, error);
        }
      }
    };
    
    fetchOptimalIndicators();
  }, [selectedCategory]);
  
  // Handle category change
  const handleCategoryChange = (value) => {
    setSelectedCategory(value);
    
    // Set first asset from the selected category as default
    if (assetCategories[value] && assetCategories[value].length > 0) {
      setSelectedAsset(assetCategories[value][0]);
    } else {
      setSelectedAsset('');
    }
  };
  
  // Handle asset change
  const handleAssetChange = (value) => {
    setSelectedAsset(value);
  };
  
  // Navigate to chart analysis page
  const goToAnalysis = () => {
    if (selectedAsset) {
      navigate(`/analysis/${selectedAsset}`);
    }
  };
  
  // Market summary columns for the table
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
          {record.trend === 'up' ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
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
  
  if (loading) {
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
      {/* Quick Analysis Section */}
      <Card className="mb-4 dashboard-card" bordered={false}>
        <Row gutter={16} align="middle">
          <Col xs={24} md={8}>
            <Select
              placeholder={t('chart_analysis.select_symbol')}
              onChange={handleCategoryChange}
              value={selectedCategory}
              style={{ width: '100%', marginBottom: '10px' }}
            >
              {Object.keys(assetCategories).map(category => (
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
              disabled={!selectedCategory}
            >
              {assetCategories[selectedCategory]?.map(asset => (
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
      {/* Market Summary Section */}
      <Row gutter={16} className="mb-4">
        <Col span={24}>
          <Card className="dashboard-card" title={t('dashboard.market_summary')} bordered={false}>
            <Table 
              dataSource={marketSummary}
              columns={marketSummaryColumns}
              rowKey="asset"
              pagination={false}
              size="middle"
            />
          </Card>
        </Col>
      </Row>
      {/* Optimal Indicators & Recent Reports Section */}
      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Card 
            className="dashboard-card" 
            title={`${t('dashboard.optimal_indicators', 'Optimal Indicators')} - ${t(`categories.${selectedCategory}`)}`}
            bordered={false}
          >
            {optimalIndicators.length > 0 ? (
              <ul className="indicator-list">
                {optimalIndicators.map((indicator, index) => (
                  <li key={index} className="indicator-item">
                    <Tag color="blue">{indicator}</Tag>
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
          <Card className="dashboard-card" title={t('dashboard.recent_reports', 'Recent Reports')} bordered={false}>
            {recentReports.length > 0 ? (
              <ul>
                {recentReports.map((report, index) => (
                  <li key={index}>
                    <a href={report.url}>{report.name}</a>
                    <Text type="secondary"> - {report.date}</Text>
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
    </div>
  );
};

export default Dashboard;