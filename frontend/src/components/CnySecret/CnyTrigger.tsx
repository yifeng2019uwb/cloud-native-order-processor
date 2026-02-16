import React, { useState } from 'react';
import CnyClaimModal from './CnyClaimModal';

const CnyTrigger: React.FC = () => {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setModalOpen(true)}
        className="text-2xl hover:scale-110 transition-transform"
        title="Red pocket"
        aria-label="Red pocket"
      >
        🧧
      </button>
      <CnyClaimModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </>
  );
};

export default CnyTrigger;
