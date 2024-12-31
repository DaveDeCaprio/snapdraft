import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from '@/components/TopNav/Header';

const AppLayout: React.FC = () => {
    return (
        <div className="min-h-screen bg-gray-50">
            <Header />
            <main className="w-full">
                {/* This will render the content of the selected section */}
                <Outlet />
            </main>
        </div>
    );
};

export default AppLayout;
