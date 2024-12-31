import React from 'react';
import { Routes, Route } from 'react-router-dom';
import DraftsList from '@/app/drafts/DraftsList.tsx';
import CreateEditDraft from '@/app/drafts/CreateEditDraft.tsx';
import ViewDraft from "@/app/drafts/ViewDraft.tsx";

const Drafts: React.FC = () => {
    return (
        <div className="container mx-auto py-4">
        <Routes>
            <Route path="/" element={<DraftsList />} />
            <Route path="create" element={<CreateEditDraft />} />
            <Route path=":draftId" element={<ViewDraft />} />
            <Route path=":draftId/edit" element={<CreateEditDraft />} />
        </Routes>
        </div>
    );
};

export default Drafts;
