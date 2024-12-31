import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { documentApi } from "@/lib/apiClient.ts"; // Adjust the import path based on your setup
import { FaEdit, FaTrash } from "react-icons/fa"; // Import FontAwesome icons

const DraftsList: React.FC = () => {
    const { id } = useParams() as { id: string; };
    const navigate = useNavigate();
    const [drafts, setDrafts] = useState<{ id: string; name: string; use_as_example?: boolean }[]>([]);
    const [documentName, setDocumentName] = useState<string>('');

    useEffect(() => {
        const fetchDocumentData = async () => {
            try {
                const response = await documentApi.readDocumentType(id);
                setDocumentName(response.data.name || '');
            } catch (error) {
                console.error("Error fetching document data:", error);
            }
        };

        const fetchDrafts = async () => {
            try {
                const response = await documentApi.readAllDrafts(id);
                setDrafts(response.data.items || []);
            } catch (error) {
                console.error("Error fetching drafts:", error);
            }
        };

        fetchDocumentData();
        fetchDrafts();
    }, [id]);

    const handleNavigateToEditor = (draftId: number) => {
        navigate(`/doc/${id}/editor/${draftId}`);
    };

    const handleEditDraft = (draftId: number) => {
        navigate(`/doc/${id}/drafts/${draftId}/edit`);
    };

    const handleCreateDraft = () => {
        navigate(`/doc/${id}/drafts/create`);
    };

    const handleDeleteDraft = async (draftId: number) => {
        try {
            await documentApi.deleteDraft(id, draftId);
            setDrafts(drafts.filter((draft) => draft.id !== draftId));
        } catch (error) {
            console.error("Error deleting draft:", error);
        }
    };

    return (
        <div className="p-4">
            <h1 className="text-2xl font-semibold mb-4">{documentName} Drafts</h1>

            <p className="mb-4 text-gray-600">
                SnapDraft can improve by learning from existing examples. Drafts marked as "Use for Training" will be
                used as examples to help SnapDraft improve.
            </p>

            <div className="mb-6">
                <table className="w-full mb-4 border-collapse">
                    <thead>
                    <tr>
                        <th className="border p-2">Name</th>
                        <th className="border p-2" style={{ width: "200px" }}>Use for Training</th>
                        <th className="border p-2" style={{ width: "100px" }}>Actions</th>
                    </tr>
                    </thead>
                    <tbody>
                    {drafts.map((draft) => (
                        <tr
                            key={draft.id}
                            className="hover:bg-gray-100 cursor-pointer"
                            onClick={() => handleNavigateToEditor(draft.id)} // Navigate to editor/<id>
                        >
                            <td className="border p-2">{draft.name}</td>
                            <td className="border p-2 text-center">
                                {draft.use_as_example ? "✔️" : ""}
                            </td>
                            <td
                                className="border p-2 text-center flex justify-center space-x-4"
                                onClick={(e) => e.stopPropagation()} // Prevents row click
                            >
                                <button
                                    onClick={() => handleEditDraft(draft.id)}
                                    className="text-blue-600 hover:text-blue-800"
                                    title="Edit Draft"
                                >
                                    <FaEdit />
                                </button>
                                <button
                                    onClick={() => handleDeleteDraft(draft.id)}
                                    className="text-red-600 hover:text-red-800"
                                    title="Delete Draft"
                                >
                                    <FaTrash />
                                </button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
                <button
                    onClick={handleCreateDraft}
                    className="mt-4 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                    Add New Draft
                </button>
            </div>
        </div>
    );
};

export default DraftsList;
