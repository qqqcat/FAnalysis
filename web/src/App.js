import React, { useState, useEffect } from 'react';
import { Layout, Menu, ConfigProvider, theme, Button } from 'antd';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { 
  LineChartOutlined, 
  DashboardOutlined, 
  AreaChartOutlined, 
  GlobalOutlined
} from '@ant-design/icons';
import './App.css';

// Pages
import Dashboard from './components/Dashboard';
import ChartAnalysis from './components/ChartAnalysis';
import DetailedReport from './components/DetailedReport';
import ApiService from './services/ApiService';

const { Header, Content, Footer, Sider } = Layout;

function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [assetCategories, setAssetCategories] = useState({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const [darkMode, setDarkMode] = useState(localStorage.getItem('theme') === 'dark');
  
  // Language switcher
  const changeLanguage = () => {
    const newLang = i18n.language === 'en' ? 'zh' : 'en';
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
  };
  
  // Theme switcher
  const toggleTheme = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('theme', newMode ? 'dark' : 'light');
  };
  
  useEffect(() => {
    const fetchAssetCategories = async () => {
      try {
        setLoading(true);
        const data = await ApiService.getAssets();
        setAssetCategories(data);
      } catch (error) {
        console.error("Failed to fetch asset categories:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAssetCategories();
    
    // Set initial language from localStorage or browser
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage) {
      i18n.changeLanguage(savedLanguage);
    }
  }, [i18n]);
  
  // Create menu items dynamically based on asset categories
  const getMenuItems = () => {
    const items = [
      {
        key: 'dashboard',
        icon: <DashboardOutlined />,
        label: t('dashboard'),
        onClick: () => navigate('/')
      }
    ];
    
    // Add categories and assets as submenu items
    if (assetCategories) {
      Object.entries(assetCategories).forEach(([category, assets]) => {
        const categoryKey = `category-${category}`;
        const categoryItem = {
          key: categoryKey,
          icon: <AreaChartOutlined />,
          label: t(`categories.${category}`),
          children: assets.map(asset => ({
            key: `asset-${asset}`,
            label: asset,
            onClick: () => navigate(`/analysis/${asset}`)
          }))
        };
        
        items.push(categoryItem);
      });
    }
    
    // Reports menu item
    items.push({
      key: 'reports',
      icon: <LineChartOutlined />,
      label: t('reports'),
      onClick: () => navigate('/reports')
    });
    
    return items;
  };
  
  return (
    <ConfigProvider
      theme={{
        algorithm: darkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
      }}
    >
      <Layout style={{ minHeight: '100vh' }}>
        <Sider 
          collapsible 
          collapsed={collapsed} 
          onCollapse={(value) => setCollapsed(value)}
        >
          <div className="logo" />
          <Menu 
            theme={darkMode ? "dark" : "light"} 
            defaultSelectedKeys={['dashboard']} 
            mode="inline" 
            items={getMenuItems()} 
          />
        </Sider>
        <Layout className="site-layout">
          <Header className="site-header">
            <div className="header-controls">
              <Button 
                icon={<GlobalOutlined />} 
                onClick={changeLanguage}
                className="lang-button"
              >
                {i18n.language === 'en' ? '中文' : 'English'}
              </Button>
              
              <Button 
                onClick={toggleTheme}
                className="theme-button"
              >
                {darkMode ? t('light_mode') : t('dark_mode')}
              </Button>
            </div>
          </Header>
          <Content style={{ margin: '0 16px' }}>
            <div className="site-content">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/analysis/:symbol" element={<ChartAnalysis />} />
                <Route path="/reports/:symbol?" element={<DetailedReport />} />
                <Route path="*" element={<Dashboard />} />
              </Routes>
            </div>
          </Content>
          <Footer style={{ textAlign: 'center' }}>
            {t('footer')} ©{new Date().getFullYear()}
          </Footer>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}

export default App;