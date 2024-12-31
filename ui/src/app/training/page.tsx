import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ModelsList from "@/app/training/ModelsList.tsx";

const Models: React.FC = () => {
    return (
        <div className="container mx-auto py-4">
        <Routes>
            <Route path="/" element={<ModelsList />} />
        </Routes>
        </div>
    );
};

export default Models;
