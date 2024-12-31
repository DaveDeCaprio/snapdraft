import React, { useEffect, useState } from 'react';
import { Link, useParams, useLocation } from 'react-router-dom';
import DocumentDropdown from './DocumentDropdown';

const Header: React.FC = () => {
    const { id } = useParams<{ id: string }>(); // Get the document ID from the URL
    const location = useLocation(); // Get the current route location
    const [selectedDoc, setSelectedDoc] = useState<string | null>(null);

    useEffect(() => {
        if (id) {
            setSelectedDoc(id);
        }
    }, [id]);

    const handleDocumentChange = (docId: string) => {
        setSelectedDoc(docId);
    };

    // Function to determine if a menu item is active
    const isActive = (path: string) => location.pathname.includes(path);

    return (
        <header className="bg-blue-600 text-white p-4 shadow-md">
            <div className="container mx-auto flex justify-start items-center space-x-6">
                <h1 className="text-xl font-semibold">SnapDraft</h1>
                {/* Document Dropdown */}
                <DocumentDropdown onChange={handleDocumentChange} />
                {/* Menu options */}
                <nav>
                    <ul className="flex space-x-4">
                        <li>
                            <Link
                                to={selectedDoc ? `/doc/${selectedDoc}/document` : '#'}
                                className={`${selectedDoc ? "hover:underline" : "text-gray-400 cursor-not-allowed"} ${isActive('/document') ? 'font-bold underline' : ''}`}
                            >
                                Document
                            </Link>
                        </li>
                        <li>
                            <Link
                                to={selectedDoc ? `/doc/${selectedDoc}/drafts` : '#'}
                                className={`${selectedDoc ? "hover:underline" : "text-gray-400 cursor-not-allowed"} ${isActive('/drafts') ? 'font-bold underline' : ''}`}
                            >
                                Drafts
                            </Link>
                        </li>
                        <li>
                            <Link
                                to={selectedDoc ? `/doc/${selectedDoc}/editor` : '#'}
                                className={`${selectedDoc ? "hover:underline" : "text-gray-400 cursor-not-allowed"} ${isActive('/editor') ? 'font-bold underline' : ''}`}
                            >
                                Editor
                            </Link>
                        </li>
                        <li>
                            <Link
                                to={selectedDoc ? `/doc/${selectedDoc}/models` : '#'}
                                className={`${selectedDoc ? "hover:underline" : "text-gray-400 cursor-not-allowed"} ${isActive('/models') ? 'font-bold underline' : ''}`}
                            >
                                Training
                            </Link>
                        </li>
                    </ul>
                </nav>
            </div>
        </header>
    );
};

export default Header;
