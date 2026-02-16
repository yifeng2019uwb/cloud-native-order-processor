import React, { useState } from 'react';
import { cnyApiService } from '@/services/cnyApi';
import type { CnyClaimResponse } from '@/types';

interface CnyClaimModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const CnyClaimModal: React.FC<CnyClaimModalProps> = ({ isOpen, onClose }) => {
  const [phrase, setPhrase] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CnyClaimResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phrase.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await cnyApiService.claim({ phrase: phrase.trim() });
      setResult(res);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const msg =
        axiosErr.response?.data?.detail ??
        (typeof axiosErr.message === 'string' ? axiosErr.message : 'Something went wrong');
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setPhrase('');
    setResult(null);
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={handleClose}
        aria-hidden="true"
      />
      {/* Modal */}
      <div
        className="relative w-full max-w-md rounded-lg border-2 border-amber-600 bg-gradient-to-b from-red-800 to-red-900 p-6 shadow-xl"
        role="dialog"
        aria-labelledby="cny-modal-title"
      >
        <button
          onClick={handleClose}
          className="absolute right-3 top-3 text-amber-200 hover:text-white"
          aria-label="Close"
        >
          ✕
        </button>
        {!result ? (
          <>
            <img
              src="/gongxifacai.jpeg"
              alt="财神爷 恭喜发财"
              className="mx-auto mb-3 max-h-32 w-auto rounded object-contain"
            />
            <h2 id="cny-modal-title" className="mb-2 text-xl font-bold text-amber-400">
              财神爷送红包
            </h2>
            <p className="mb-4 text-sm text-amber-100/90">
              Enter a secret word or phrase to claim!
            </p>
            <form onSubmit={handleSubmit}>
              <input
                type="text"
                value={phrase}
                onChange={(e) => setPhrase(e.target.value)}
                placeholder="Enter secret or magic phrase"
                className="mb-3 w-full rounded border border-amber-600 bg-amber-50/10 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500"
                disabled={loading}
              />
              {error && (
                <p className="mb-3 text-sm text-amber-200">{error}</p>
              )}
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded bg-amber-600 px-4 py-2 font-medium text-white hover:bg-amber-500 disabled:opacity-70"
              >
                {loading ? 'Checking...' : '领取红包 / Claim'}
              </button>
            </form>
          </>
        ) : (
          <div className="text-center">
            {/* Red pocket card - amount at bottom to avoid covering god's face */}
            <div className="mx-auto mb-4 inline-block">
              <div
                className={`relative flex min-h-[200px] flex-col overflow-hidden rounded-lg border-2 border-amber-500 bg-cover bg-top bg-no-repeat shadow-inner ${
                  result.got_red_pocket ? 'max-w-[220px] w-[220px]' : 'max-w-[180px] w-[180px]'
                }`}
                style={{
                  backgroundImage: result.got_red_pocket
                    ? "url('/bigrpocket.jpg')"
                    : "url('/littleredpocket.jpg')",
                }}
              >
                {result.got_red_pocket && (
                  <div className="px-2 pt-2 text-center">
                    <p className="text-xs font-medium uppercase tracking-wide text-amber-300/90">
                      大红包 Opened!
                    </p>
                    <p className="text-[10px] text-amber-200/80">Big Red Pocket</p>
                  </div>
                )}
                <div className="mt-auto flex flex-col items-center justify-end px-2 pb-3 pt-2">
                  <p className="text-2xl font-bold text-amber-200 drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)]">
                    ${(typeof result.amount === 'number' ? result.amount : parseFloat(String(result.amount)) || 0).toFixed(2)}
                  </p>
                </div>
              </div>
            </div>
            <p className="mb-4 text-base font-bold text-amber-400">
              {result.got_red_pocket ? '恭喜发财！' : '谢谢参与！'}
            </p>
            <button
              onClick={handleClose}
              className="rounded bg-amber-600 px-4 py-2 font-medium text-white hover:bg-amber-500"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CnyClaimModal;
