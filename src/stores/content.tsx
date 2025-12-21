import { createContext, useContext, createSignal, createEffect, ParentComponent } from 'solid-js';
import { fetchPortfolioData } from '../data/mock-api';
import { lang } from './i18n';
import type { PortfolioData } from '../types/portfolio';

interface PortfolioContextValue {
  data: () => PortfolioData | undefined;
  loading: () => boolean;
  refetch: () => void;
}

const PortfolioContext = createContext<PortfolioContextValue>();

export const PortfolioProvider: ParentComponent = (props) => {
  const [portfolioData, setPortfolioData] = createSignal<PortfolioData | undefined>(undefined);
  const [loading, setLoading] = createSignal(true);

  const loadData = async (language: string) => {
    setLoading(true);
    try {
      const data = await fetchPortfolioData(language as 'en' | 'pt');
      setPortfolioData(data);
    } finally {
      setLoading(false);
    }
  };

  // Load on mount and when language changes
  createEffect(() => {
    const currentLang = lang();
    void loadData(currentLang);
  });

  const refetch = () => void loadData(lang());

  return (
    <PortfolioContext.Provider value={{ 
      data: portfolioData, 
      loading,
      refetch 
    }}>
      {props.children}
    </PortfolioContext.Provider>
  );
};

export const usePortfolio = () => {
  const context = useContext(PortfolioContext);
  if (!context) {
    throw new Error('usePortfolio must be used within a PortfolioProvider');
  }
  
  // Return compatible interface
  const data = Object.assign(context.data, {
    get loading() {
      return context.loading();
    }
  });
  
  return { data, refetch: context.refetch };
};
