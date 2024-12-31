import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { DraftDocumentRead } from '@/generated/api';
import {documentApi, filesApi} from "@/lib/apiClient.ts";

const ViewDraft: React.FC = () => {
    const { id, draftId } = useParams();
    const navigate = useNavigate();
    const [draft, setDraft] = useState<DraftDocumentRead | null>(null);
    const [documentName, setDocumentName] = useState<string>('');
    const [sourceDocuments, setSourceDocuments] = useState<{ [key: number]: string }>({});
    const [fileNames, setFileNames] = useState<{ [key: number]: string }>({});

    useEffect(() => {
        const fetchDraft = async () => {
            try {
                // Fetch document type details to get the name
                const documentResponse = await documentApi.readDocumentType(Number(id));
                setDocumentName(documentResponse.data.name || '');

                // Fetch example details
                const response = await documentApi.readDraftDocument(Number(id), Number(draftId));
                setDraft(response.data);

                // Fetch source document names from the document type
                const sourceDocs = documentResponse.data.source_docs;
                const newSourceDocuments = sourceDocs.reduce((acc: { [key: number]: string }, doc: any) => {
                    acc[doc.id] = doc.name;
                    return acc;
                }, {});
                setSourceDocuments(newSourceDocuments);

                // Fetch file names
                const fileIds = response.data.source_files.map(file => file.file_id).concat(response.data.output_file_id);
                const filePromises = fileIds.map(fileId => filesApi.readStoredFile(fileId));
                const fileResponses = await Promise.all(filePromises);
                const newFileNames = fileResponses.reduce((acc, res) => {
                    acc[res.data.id] = res.data.original_filename;
                    return acc;
                }, {} as { [key: number]: string });
                setFileNames(newFileNames);

            } catch (error) {
                console.error('Error fetching draft details:', error);
            }
        };
        fetchDraft();
    }, [id, draftId]);

    const handleEditDraft = () => {
        navigate(`/doc/${id}/examples/${draftId}/edit`);
    };

    const handleDeleteDraft = async () => {
        try {
            if (draftId) {
                await documentApi.deleteDraftDocument(Number(id), Number(draftId));
                navigate(`/doc/${id}/drafts`);
            }
        } catch (error) {
            console.error('Error deleting draft:', error);
        }
    };

    if (!draft) {
        return <div>Loading...</div>;
    }

    return (
        <div className="p-4">
            {/* Header with Link */}
            <div className="flex items-center text-2xl font-semibold mb-4">
                <span
                    className="cursor-pointer text-blue-600 hover:underline mr-4"
                    onClick={() => navigate(`/doc/${id}/drafts`)}
                >
                    Drafts for {documentName}
                </span>
                <span>&gt; {draft.name}</span>
            </div>

            {/* Source Files Section */}
            <div className="mb-6">
                <h2 className="text-xl font-semibold mb-2">Source Files:</h2>
                <ul>
                    {draft.source_files.map((file, index) => (
                        <li key={index} className="mb-2">
                            <strong>{sourceDocuments[file.source_document_id] || 'Unknown Source Document'}:</strong> {fileNames[file.file_id] || 'Unknown File'}
                        </li>
                    ))}
                </ul>
            </div>

            {/* Output File Section */}
            <div className="mb-6">
                <h2 className="text-xl font-semibold mb-2">Output File:</h2>
                <p>{fileNames[draft.output_file_id] || 'Unknown File'}</p>
            </div>

            {/* Navigation Buttons */}
            <button
                onClick={handleEditDraft}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
                Edit Draft
            </button>
            <button
                onClick={handleDeleteDraft}
                className="mt-4 ml-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
                Delete Draft
            </button>
        </div>
    );
};

export default ViewDraft;
