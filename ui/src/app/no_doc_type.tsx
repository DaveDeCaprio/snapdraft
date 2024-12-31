import React from 'react';
import Header from '@/components/TopNav/Header.tsx';

const MainPage: React.FC = () => {
    return (
        <div className="min-h-screen bg-gray-50">
            <Header />
            <main className="container mx-auto py-10">
                <div className="text-center text-gray-800">
                    <p className="text-lg font-medium">Select a document type to start writing or editing.</p>
                </div>
            </main>
        </div>
    );
};

export default MainPage;
