import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation resources
import enTranslation from './locales/en/translation.json';
import zhTranslation from './locales/zh/translation.json';

const resources = {
  en: {
    translation: enTranslation
  },
  zh: {
    translation: zhTranslation
  }
};

i18n
  // detect user language
  .use(LanguageDetector)
  // pass the i18n instance to react-i18next
  .use(initReactI18next)
  // init i18next
  .init({
    resources,
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    interpolation: {
      escapeValue: false, // not needed for react as it escapes by default
    }
  });

export default i18n;