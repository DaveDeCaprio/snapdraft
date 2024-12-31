import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate  } from 'react-router-dom';
import LoginPage from '@/app/login/page';
import NoDocTypePage from '@/app/no_doc_type.tsx';
import Document from '@/app/document/page';
import EditorPage from '@/app/editor/page';
import AppLayout from "@/app/layout.tsx";
import Drafts from "@/app/drafts/page.tsx";
import Models from "@/app/training/page.tsx";

const App: React.FC = () => {
    const isLoggedIn = localStorage.getItem('username'); // Check login status from local storage

    return (
        <Router>
            <Routes>
                {/* If user is logged in, redirect to /main, otherwise show Login page */}
                <Route path="/" element={isLoggedIn ? <Navigate to="/no_doc_type" /> : <LoginPage />} />

                {/* Main page route */}
                <Route path="/no_doc_type" element={<NoDocTypePage />} />

                {/* Routes for the document-related pages wrapped inside the DocumentLayout */}
                <Route path="/doc/:id" element={<AppLayout />}>
                    <Route path="drafts/*" element={<Drafts />} />
                    <Route path="document" element={<Document />} />
                    <Route path="editor/:draftId?" element={<EditorPage />} />
                    <Route path="models/*" element={<Models />} />
                </Route>
            </Routes>
          </Router>
  );
};

export default App;