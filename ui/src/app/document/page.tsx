import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { documentApi } from "@/lib/apiClient.ts"; // Adjust the import path based on your setup
import FileEditor from "@/components/FileEditor"; // Import FileEditor component

const Document: React.FC = () => {
    const { id } = useParams() as { id: string; };
    const navigate = useNavigate();
    const [name, setName] = useState("");
    const [instructions, setInstructions] = useState("");
    const [sources, setSources] = useState<{ id?: string; name: string; description: string }[]>([]);
    const [newSource, setNewSource] = useState<{ name: string; description: string }>({
        name: "",
        description: "",
    });
    const [templateFileId, setTemplateFileId] = useState<string | null>(null);

    useEffect(() => {
        const fetchDocumentData = async () => {
            try {
                const response = await documentApi.readDocumentType(id);
                setName(response.data.name || "");
                setInstructions(response.data.instructions || "");
                setSources(response.data.sources || []);
                setTemplateFileId(response.data.template_file_id || null);
            } catch (error) {
                console.error("Error fetching document data:", error);
            }
        };
        fetchDocumentData();
    }, [id]);

    const handleInstructionsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInstructions(e.target.value);
    };

    const handleSourceDocChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setNewSource((prev) => ({ ...prev, [name]: value }));
    };

    const handleAddSourceDoc = () => {
        if (newSource.name.trim() && newSource.description.trim()) {
            setSources((prev) => [...prev, newSource]);
            setNewSource({ name: "", description: "" });
        }
    };

    const handleDeleteSourceDoc = (index: number) => {
        setSources((prev) => prev.filter((_, i) => i !== index));
    };

    const handleSaveChanges = async () => {
        try {
            await documentApi.updateDocumentType(id, {
                name,
                instructions,
                sources,
                template_file_id: templateFileId,
            });
            navigate(`/doc/${id}/drafts`);
        } catch (error) {
            console.error("Error saving changes:", error);
        }
    };

    const handleDeleteDocument = async () => {
        if (confirm(`Are you sure you want to delete the document "${name}"?`)) {
            try {
                await documentApi.deleteDocumentType(id);
                alert("Document deleted successfully!");
                navigate("/no_doc_type"); // Adjust the path based on your app's routing
            } catch (error) {
                console.error("Error deleting document:", error);
                alert("Failed to delete the document.");
            }
        }
    };

    return (
        <div className="container mx-auto p-4">
            <div className="mb-6">
                <label className="text-xl font-semibold mb-2" htmlFor="instructions">
                    Instructions
                </label>
                <p className="mb-4 text-gray-600">
                    Describe the document to be created and any special instructions for how to generate it from the
                    source documents.
                </p>
                <textarea
                    id="instructions"
                    value={instructions}
                    onChange={handleInstructionsChange}
                    rows={4}
                    className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
            </div>

            <div className="mb-6">
                <label className="text-xl font-semibold mb-2" htmlFor="template-file">
                    Template
                </label>
                <p className="mt-2 text-gray-600">
                    A template shows the desired structure for the document, with placeholders and/or instructions for
                    each section.
                </p>
                <FileEditor
                    fileId={templateFileId}
                    onFileIdChange={(newFileId) => setTemplateFileId(newFileId)}
                />
            </div>

            <div className="mb-6">
                <h2 className="text-xl font-semibold mb-2">Source Documents</h2>
                <p className="mb-4 text-gray-600">
                    List the types of source documents that will be provided for each example. For each, provide a name
                    and a short description.
                </p>
                <table className="w-full mb-4 border-collapse">
                    <thead>
                    <tr>
                        <th className="border p-2 w-1/6">Name</th>
                        <th className="border p-2">Description</th>
                        <th className="border p-2 w-1/12"></th>
                    </tr>
                    </thead>
                    <tbody>
                    {sources.map((doc, index) => (
                        <tr key={index}>
                            <td className="border p-2 truncate">{doc.name}</td>
                            <td className="border p-2">{doc.description}</td>
                            <td className="border p-2 text-center">
                                <button
                                    onClick={() => handleDeleteSourceDoc(index)}
                                    className="px-2 py-1 bg-red-500 text-white rounded-md hover:bg-red-600"
                                >
                                    X
                                </button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
                <div className="flex gap-2">
                    <input
                        type="text"
                        name="name"
                        value={newSource.name}
                        onChange={handleSourceDocChange}
                        placeholder="Source Document Name"
                        maxLength={30}
                        className="w-1/4 p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                        type="text"
                        name="description"
                        value={newSource.description}
                        onChange={handleSourceDocChange}
                        placeholder="Source Document Description"
                        className="w-3/4 p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                        onClick={handleAddSourceDoc}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                    >
                        Add
                    </button>
                </div>
            </div>

            <div className="flex gap-4">
                <button
                    onClick={handleSaveChanges}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                    Save Changes
                </button>
                <button
                    onClick={handleDeleteDocument}
                    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                    Delete Document
                </button>
            </div>
        </div>
    );
};

export default Document;
