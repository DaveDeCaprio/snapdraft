import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { documentApi } from "@/lib/apiClient.ts";
import FileEditor from "@/components/FileEditor";
import { SourceType } from "@/generated/api";

const CreateEditDraft: React.FC = () => {
    const { id, draftId } = useParams() as { id: string; draftId: string };
    const navigate = useNavigate();

    const [documentName, setDocumentName] = useState("");
    const [sources, setSources] = useState<SourceType[]>([]);
    const [name, setName] = useState("");
    const [useForTraining, setUseForTraining] = useState(false);
    const [outputFileId, setOutputFileId] = useState<string | null>(null);
    const [sourceFileIds, setSourceFileIds] = useState<{ [key: string]: string | null }>({});

    useEffect(() => {
        const fetchDocumentData = async () => {
            try {
                // Fetch document type to get its name
                const response = await documentApi.readDocumentType(id);
                setDocumentName(response.data.name);
                setSources(response.data.sources || []);

                if (draftId) {
                    // Fetch draft details if we are editing
                    const draftResponse = await documentApi.readDraft(id, draftId);
                    setName(draftResponse.data.name);
                    setUseForTraining(draftResponse.data.use_for_training || false);

                    setSourceFileIds(draftResponse.data.source_file_ids || {});
                    setOutputFileId(draftResponse.data.output_file_id || null);
                }
            } catch (error) {
                console.error("Error fetching document or draft data:", error);
            }
        };
        fetchDocumentData();
    }, [id, draftId]);

    const handleSaveDraft = async () => {
        try {
            const draftData = {
                name,
                use_for_training: useForTraining,
                output_file_id: outputFileId,
                source_file_ids: sourceFileIds,
            };

            // Create or update draft
            if (draftId) {
                await documentApi.updateDraft(id, draftId, draftData);
            } else {
                await documentApi.createDraft(id, draftData);
            }
            navigate(`/doc/${id}/drafts`);
        } catch (error) {
            console.error("Error saving draft:", error);
        }
    };

    const handleCancel = () => {
        navigate(`/doc/${id}/drafts`);
    };

    return (
        <div className="p-4">
            <h1 className="text-2xl font-semibold mb-4">
                {draftId ? `Edit "${documentName}" Draft` : `Create New "${documentName}" Draft`}
            </h1>

            {/* Draft Name Input */}
            <div className="mb-6">
                <label className="block text-lg font-medium mb-2" htmlFor="draftName">
                    Draft Name:
                </label>
                <input
                    id="draftName"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
            </div>

            {/* Source Files */}
            <div className="mb-6">
                <h2 className="text-xl font-semibold mb-2">Source Files</h2>
                {sources.map((source) => (
                    <div key={source.name} className="mb-4 flex items-center gap-4">
                        <label className="text-lg font-medium w-1/4">{source.name}</label>
                        <div className="w-3/4">
                            <FileEditor
                                fileId={sourceFileIds[source.name!] || null}
                                onFileIdChange={(newFileId) =>
                                    setSourceFileIds((prev) => ({
                                        ...prev,
                                        [source.name!]: newFileId,
                                    }))
                                }
                            />
                        </div>
                    </div>
                ))}
            </div>

            {/* Output File */}
            <div className="mb-6">
                <h2 className="text-xl font-semibold mb-2">Output File</h2>
                <p className="mt-2 text-gray-600">
                    If you provide an output file, that can be used as a draft to generate an improved version, or as an
                    example to train SnapDraft.
                </p>
                <FileEditor
                    fileId={outputFileId}
                    onFileIdChange={setOutputFileId}
                />
            </div>

            {/* Use for Training Checkbox */}
            <div className="mb-6 flex items-center gap-2">
                <input
                    type="checkbox"
                    id="useForTraining"
                    checked={useForTraining}
                    onChange={(e) => setUseForTraining(e.target.checked)}
                    disabled={!outputFileId}
                    className="h-5 w-5"
                />
                <label htmlFor="useForTraining" className="text-lg font-medium">
                    Use for Training
                </label>
            </div>

            {/* Buttons */}
            <div className="mt-4">
                <button
                    onClick={handleSaveDraft}
                    className="mr-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                    {draftId ? "Update Draft" : "Create Draft"}
                </button>
                <button
                    onClick={handleCancel}
                    className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                >
                    Cancel
                </button>
            </div>
        </div>
    );
};

export default CreateEditDraft;
