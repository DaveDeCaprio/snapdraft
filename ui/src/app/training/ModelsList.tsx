import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { documentApi, generatorsApi } from "@/lib/apiClient.ts"; // Adjust the import path based on your setup
import { FaTrash } from "react-icons/fa";
import { Model } from "ckeditor5"; // Import FontAwesome icons
import { format } from 'date-fns';

const ModelsList: React.FC = () => {
    const { id } = useParams() as { id: string; };
    const [models, setModels] = useState<Model[]>([]);
    const [documentName, setDocumentName] = useState<string>('');
    const [generators, setGenerators] = useState<string[]>([]);
    const [selectedGenerator, setSelectedGenerator] = useState<string>('');
    const [showDialog, setShowDialog] = useState<boolean>(false);

    useEffect(() => {
        const fetchDocumentData = async () => {
            try {
                const response = await documentApi.readDocumentType(id);
                setDocumentName(response.data.name || '');
            } catch (error) {
                console.error("Error fetching document data:", error);
            }
        };

        const fetchModels = async () => {
            try {
                const response = await documentApi.readAllModels(id);
                setModels(response.data.items || []);
            } catch (error) {
                console.error("Error fetching models:", error);
            }
        };

        const fetchGenerators = async () => {
            try {
                const response = await generatorsApi.readAllGenerators();
                setGenerators(response.data.items.map(g => g.name) || []);
            } catch (error) {
                console.error("Error fetching generators:", error);
            }
        };

        fetchDocumentData();
        fetchModels();
        fetchGenerators();
    }, [id]);

    const handleCreateModel = async () => {
        try {
            const newModel = await documentApi.createModel(id, {generator:selectedGenerator});
            setModels((prevModels) => [...prevModels, newModel.data]);
            setShowDialog(false);
        } catch (error) {
            console.error("Error creating model:", error);
        }
    };

    const handleSetActive = async (modelId: string) => {
        try {
            await documentApi.setActiveModel(id, modelId);
            const response = await documentApi.readAllModels(id);
            setModels(response.data.items || []);
        } catch (error) {
            console.error("Error setting default model:", error);
        }
    };

    const handleDeleteModel = async (modelId: string) => {
        try {
            await documentApi.deleteModel(id, modelId);
            setModels(models.filter((model) => model.id !== modelId));
        } catch (error) {
            console.error("Error deleting model:", error);
        }
    };

    return (
        <div className="p-4">
            <h1 className="text-2xl font-semibold mb-4">{documentName} Models</h1>

            <div className="mb-6">
                <table className="w-full mb-4 border-collapse">
                    <thead>
                    <tr>
                        <th className="border p-2">Version</th>
                        <th className="border p-2">Is Active</th>
                        <th className="border p-2">Generator</th>
                        <th className="border p-2">Created At</th>
                        <th className="border p-2">Status</th>
                        <th className="border p-2">Num Examples</th>
                        <th className="border p-2" style={{ width: "100px" }}>Actions</th>
                    </tr>
                    </thead>
                    <tbody>
                    {models.map((model) => (
                        <tr
                            key={model.id}
                            className="hover:bg-gray-100"
                        >
                            <td className="border p-2">{model.version}</td>
                            <td className="border p-2">{model.is_active ? 'X' : ''}</td>
                            <td className="border p-2 text-center">{model.generator}</td>
                            <td className="border p-2 text-center">
                                {format(new Date(model.created_at), 'MM/dd/yyyy h:mma').toLowerCase()}
                            </td>
                            <td className="border p-2 text-center">
                                {model.status}
                            </td>
                            <td className="border p-2 text-center">
                                {model.draft_ids.length}
                            </td>
                            <td
                                className="border p-2 text-center flex justify-center space-x-4"
                                onClick={(e) => e.stopPropagation()} // Prevents row click
                            >
                                <button
                                    onClick={() => handleSetActive(model.id)}
                                    title="Set as Active"
                                    className="px-2 rounded-md bg-green-400 text-white"
                                >
                                    Make Default
                                </button>
                                <button
                                    onClick={() => handleDeleteModel(model.id)}
                                    className="text-red-600 hover:text-red-800"
                                    title="Delete Model"
                                >
                                    <FaTrash />
                                </button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
                <button
                    onClick={() => setShowDialog(true)}
                    className="mt-4 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                    Train New Model
                </button>
            </div>

            {showDialog && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex justify-center items-center">
                    <div className="bg-white p-6 rounded-lg shadow-lg">
                        <h2 className="text-xl mb-4">Select Generator</h2>
                        <select
                            value={selectedGenerator}
                            onChange={(e) => setSelectedGenerator(e.target.value)}
                            className="mb-4 p-2 border rounded w-full"
                        >
                            <option value="" disabled>Select a generator</option>
                            {generators.map((gen) => (
                                <option key={gen} value={gen}>{gen}</option>
                            ))}
                        </select>
                        <div className="flex justify-end space-x-4">
                            <button
                                onClick={() => setShowDialog(false)}
                                className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleCreateModel}
                                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                                disabled={!selectedGenerator}
                            >
                                Train
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ModelsList;
