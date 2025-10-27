import { useState, useEffect, useCallback } from 'react';
import { inventoryApiService } from '@/services/inventoryApi';
import type {
  Asset,
  AssetDetail,
  AssetListRequest,
  InventoryApiError
} from '@/types';

interface UseInventoryState {
  assets: Asset[];
  loading: boolean;
  error: InventoryApiError | null;
  totalCount: number;
  activeCount: number;
  filteredCount: number;
}

interface UseInventoryReturn extends UseInventoryState {
  listAssets: (params?: AssetListRequest) => Promise<void>;
  getAssetById: (assetId: string) => Promise<AssetDetail | null>;
  refreshAssets: () => Promise<void>;
  clearError: () => void;
}

export const useInventory = (): UseInventoryReturn => {
  const [state, setState] = useState<UseInventoryState>({
    assets: [],
    loading: false,
    error: null,
    totalCount: 0,
    activeCount: 0,
    filteredCount: 0
  });

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const listAssets = useCallback(async (params?: AssetListRequest) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await inventoryApiService.listAssets(params);
      setState(prev => ({
        ...prev,
        assets: response.data,  // Backend returns 'data' not 'assets'
        totalCount: response.total_count,
        activeCount: response.active_count,
        filteredCount: response.data.length,  // Use data length for filtered count
        loading: false,
        error: null
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error as InventoryApiError
      }));
    }
  }, []);

  const getAssetById = useCallback(async (assetId: string): Promise<AssetDetail | null> => {
    try {
      const asset = await inventoryApiService.getAssetById(assetId);
      return asset;
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error as InventoryApiError
      }));
      return null;
    }
  }, []);

  const refreshAssets = useCallback(async () => {
    await listAssets();
  }, [listAssets]);

  // Load assets on mount
  useEffect(() => {
    // Always fetch all assets for frontend pagination - no limit
    listAssets({ active_only: true, limit: undefined });
  }, [listAssets]);

  return {
    ...state,
    listAssets,
    getAssetById,
    refreshAssets,
    clearError
  };
};

// Hook for individual asset details
export const useAssetDetail = (assetId: string | null) => {
  const [asset, setAsset] = useState<AssetDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<InventoryApiError | null>(null);

  const fetchAsset = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);

    try {
      const assetData = await inventoryApiService.getAssetById(id);
      setAsset(assetData);
    } catch (err) {
      setError(err as InventoryApiError);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (assetId) {
      fetchAsset(assetId);
    } else {
      setAsset(null);
      setError(null);
    }
  }, [assetId, fetchAsset]);

  return { asset, loading, error, refetch: () => assetId && fetchAsset(assetId) };
};