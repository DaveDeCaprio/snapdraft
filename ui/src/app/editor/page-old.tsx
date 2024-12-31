import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { documentApi, filesApi } from '@/lib/apiClient.ts';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import DraftCombobox from "@/components/DraftCombobox.tsx";
import Editor from "@/app/editor/Editor.tsx";

const Playground: React.FC = () => {
    const { id } = useParams();
    const [documentName, setDocumentName] = useState<string>('');
    const [drafts, setDrafts] = useState<{ value: number; label: string }[]>([]);
    const [selectedDraft, setSelectedDraft] = useState<{ value: number; label: string } | null>(null);
    const [sourceDocs, setSourceDocs] = useState<{ id: number; name: string }[]>([]);
    const [sourceFiles, setSourceFiles] = useState<{ [key: string]: File | null }>({});
    const [generatedText, setGeneratedText] = useState<string>('');
    const [selectedOption, setSelectedOption] = useState<string>('draft');
    const [chatInput, setChatInput] = useState<string>('');
    const [chatMessages, setChatMessages] = useState<{ user: string; message: string }[]>([]);
    const [isGenerating, setIsGenerating] = useState<boolean>(false);
    const [showSaveDialog, setShowSaveDialog] = useState<boolean>(false);
    const [newExampleName, setNewExampleName] = useState<string>('');
    const [savedSourceFilesData, setSavedSourceFilesData] = useState<{ source_document_id: number; file_id: number }[]>([]);

    useEffect(() => {
        const fetchDocumentData = async () => {
            try {
                // Fetch document type details to get the name and source documents
                const response = await documentApi.readDocumentType(Number(id));
                setDocumentName(response.data.name || '');
                setSourceDocs(response.data.source_docs || []);

                // Fetch examples for the document type
                const draftsResponse = await documentApi.readAllDraftDocuments(Number(id));
                setDrafts(
                    draftsResponse.data.map((example: any) => ({
                        value: example.id,
                        label: example.name,
                    }))
                );
            } catch (error) {
                console.error('Error fetching document data:', error);
            }
        };
        fetchDocumentData();
    }, [id]);

    const handleSourceFileChange = (e: React.ChangeEvent<HTMLInputElement>, key: string) => {
        if (e.target.files && e.target.files.length > 0) {
            setSourceFiles({ ...sourceFiles, [key]: e.target.files[0] });
        }
    };

    const handleGenerateDocument = async () => {
        try {
            setIsGenerating(true);
            setGeneratedText('');
            setChatInput('');
            setChatMessages([]);

            let sourceFilesData = [];
            if (selectedOption === 'draft' && selectedDraft) {
                // Use existing example to generate document
                const response = await documentApi.readDraftDocument(Number(id), selectedDraft.value);
                sourceFilesData = response.data.source_files;
            } else if (selectedOption === 'new') {
                // Upload source files and generate a new document
                const uploadedSourceFiles = await Promise.all(
                    Object.entries(sourceFiles).map(async ([key, file]) => {
                        if (file) {
                            const uploadedFileId = await filesApi.uploadFile(file);
                            return { source_document_id: Number(key), file_id: uploadedFileId.data.id };
                        }
                        return null;
                    })
                );

                sourceFilesData = uploadedSourceFiles.filter(
                    (file): file is { source_document_id: number; file_id: number } => file !== null
                );
            }
            setSavedSourceFilesData(sourceFilesData);

            // Generate the document using the collected source files data
            const generationInputs = { source_files: sourceFilesData };
            const generateResponse = await documentApi.generateDocument(Number(id), generationInputs);
            setGeneratedText(generateResponse.data.text);
        } catch (error) {
            console.error('Error generating document:', error);
        } finally {
            setIsGenerating(false);
        }
    };

    const handleChatSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (chatInput.trim() && generatedText.trim()) {
            try {
                setIsGenerating(true);

                // Call the regenerate_document API with the current generated text and the chat input
                const regenerateResponse = await documentApi.regenerateDocument(
                    Number(id),
                    {
                        source_files: savedSourceFilesData,
                        current_text: generatedText,
                        feedback: chatInput,
                    }
                );

                // Update the generated text and chat messages based on the response
                setGeneratedText(regenerateResponse.data.text);
                setChatMessages([
                    ...chatMessages,
                    { user: 'User', message: chatInput },
                    { user: 'System', message: regenerateResponse.data.message }
                ]);
                setChatInput('');
            } catch (error) {
                console.error('Error regenerating document:', error);
            } finally {
                setIsGenerating(false);
            }
        }
    };

    const handleSelectDraft = (draftId: { value: number; label: string; }) => {
        setSelectedDraft(draftId);
        setGeneratedText("");
        setChatInput("");
        setChatMessages([]);
    };

    const handleSaveNewExample = () => {
        setShowSaveDialog(true);
    };

    const handleSaveDialogClose = () => {
        setShowSaveDialog(false);
        setNewExampleName('');
    };

    const handleSaveDialogSubmit = async () => {
        if (newExampleName.trim()) {
            // Logic to save the generated text as a new example
            try {
                const textBlob = new Blob([generatedText], { type: 'text/plain' });
                const textFile = new File([textBlob], 'output.txt', { type: 'text/plain' });

                const outputFileId = await filesApi.uploadFile(textFile);
                await documentApi.createDraftDocument(
                    Number(id),
                    {
                        name: newExampleName,
                        source_files: savedSourceFilesData,
                        output_file_id: outputFileId.data.id,
                        use_as_example: true,
                    }
                );
                alert('New example saved successfully!');

                // Clear all relevant states
                setGeneratedText('');
                setChatInput('');
                setChatMessages([]);
                setSourceFiles({});
                setSavedSourceFilesData([]);
                setSourceDocs((prevSourceDocs) =>
                    prevSourceDocs.map((doc) => ({ ...doc, key: Math.random().toString() }))
                );
            } catch (error) {
                console.error('Error saving new example:', error);
                alert('Failed to save new example.');
            }
            handleSaveDialogClose();
        }
    };

    return (
        <div className="flex h-full">
            {/* Left Sidebar */}
            <div className="w-1/4 p-4 bg-gray-100 border-r border-gray-300">
                {/* Document Selection */}
                <div className="mb-6">
                    <h2 className="text-lg font-semibold mb-2">Document</h2>
                    <select
                        value={id}
                        onChange={(e) => navigate(`/doc/${e.target.value}/drafts`)}
                        className="w-full p-2 border rounded-md"
                    >
                        {/* Example options - Replace with dynamic document list */}
                        <option value="1">Document 1</option>
                        <option value="2">Document 2</option>
                        <option value="3">Document 3</option>
                    </select>
                </div>

                {/* Feedback Section */}
                <div>
                    <h2 className="text-lg font-semibold mb-2">Feedback</h2>
                    <p className="text-gray-600">
                        SnapDraft can improve by learning from examples. Drafts marked as "Use for Training" will help
                        improve
                        SnapDraft's recommendations.
                    </p>
                </div>
            </div>

            {/* Main Content - Editor Panel */}
            <div className="flex-1 p-4">
                <h1 className="text-2xl font-semibold mb-4">Drafts for {documentName}</h1>

                <div className="mb-6">
                    <table className="w-full mb-4 border-collapse">
                        <thead>
                        <tr>
                            <th className="border p-2 text-left" style={{width: "auto"}}>Name</th>
                            {hasSections && <th className="border p-2 text-left">Section</th>}
                            <th className="border p-2 text-center" style={{width: "150px"}}>Use for Training</th>
                            <th className="border p-2 text-center" style={{width: "50px"}}>Actions</th>
                        </tr>
                        </thead>
                        <tbody>
                        {drafts.map((draft) => (
                            <tr
                                key={draft.id}
                                className="hover:bg-gray-100 cursor-pointer"
                                onClick={() => handleViewDraft(draft.id)}
                            >
                                <td className="border p-2">{draft.name}</td>
                                {hasSections && <td className="border p-2">{draft.section_name || "N/A"}</td>}
                                <td className="border p-2 text-center">
                                    {draft.use_as_example ? "✔️" : ""}
                                </td>
                                <td
                                    className="border p-2 text-center"
                                    onClick={(e) => e.stopPropagation()} // Prevents row click
                                >
                                    <button
                                        onClick={() => handleDeleteDraft(draft.id)}
                                        className="text-red-600 hover:text-red-800 font-bold"
                                        title="Delete Draft"
                                    >
                                        X
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
        </div>
    );
    // return (
    //     <div className="p-0">
    //         <div className="mb-6 w-full">
    //             <h1 className="text-2xl font-semibold mb-2">Playground for {documentName}</h1>
    //
    //             <RadioGroup value={selectedOption} onValueChange={setSelectedOption} className="mb-6">
    //                 <div className="flex items-center gap-8">
    //                     <div className="flex items-center gap-2">
    //                         <RadioGroupItem value="draft" id="use-draft" />
    //                         <label htmlFor="use-draft" className="text-lg font-medium">
    //                             Use Existing Draft
    //                         </label>
    //                     </div>
    //                     <div className="flex items-center gap-2">
    //                         <RadioGroupItem value="new" id="generate-new" />
    //                         <label htmlFor="generate-new" className="text-lg font-medium">
    //                             Generate New Document
    //                         </label>
    //                     </div>
    //                 </div>
    //             </RadioGroup>
    //
    //             {selectedOption === 'draft' && (
    //                 <div className="flex items-center gap-4 mb-4">
    //                     <DraftCombobox
    //                         drafts={drafts}
    //                         selectedDraft={selectedDraft}
    //                         setSelectedDraft={handleSelectDraft}
    //                     />
    //                     <button
    //                         onClick={handleGenerateDocument}
    //                         className={`px-4 py-2 rounded-md ${
    //                             isGenerating
    //                                 ? 'bg-blue-400 text-white cursor-not-allowed'
    //                                 : 'bg-blue-600 text-white hover:bg-blue-700'
    //                         }`}
    //                         disabled={isGenerating}
    //                     >
    //                         Generate
    //                     </button>
    //                 </div>
    //             )}
    //
    //             {selectedOption === 'new' && (
    //                 <div className="flex items-center gap-4">
    //                     <div className="mt-4">
    //                         {sourceDocs.map((doc) => (
    //                             <div key={doc.key || doc.id} className="mb-4 flex items-center gap-4">
    //                                 <label className="text-sm font-medium">{doc.name}:</label>
    //                                 <input
    //                                     key={doc.key || doc.id} // Use the key to force re-render
    //                                     type="file"
    //                                     onChange={(e) => handleSourceFileChange(e, String(doc.id))}
    //                                     className="p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    //                                 />
    //                             </div>
    //                         ))}
    //                     </div>
    //                     <button
    //                         onClick={handleGenerateDocument}
    //                         className={`px-4 py-2 rounded-md ${
    //                             isGenerating
    //                                 ? 'bg-blue-400 text-white cursor-not-allowed'
    //                                 : 'bg-blue-600 text-white hover:bg-blue-700'
    //                         }`}
    //                         disabled={isGenerating}
    //                     >
    //                         Generate
    //                     </button>
    //                 </div>
    //             )}
    //             <h2 className="text-gray-600 mt-4 mb-4">You can edit the text below, or ask SnapDraft to update it based on your feedback.</h2>
    //             <div className="border-t-2 border-gray-300 mt-4 mb-4"/>
    //         </div>
    //
    //         {/* Content Section with Generated Text and Chat */}
    //         <div className="flex">
    //             {/* Generated Text Section */}
    //             <div className="w-2/3 pr-4">
    //                 <Editor />
    //                 <div className="mt-0">
    //                     <textarea
    //                         value={generatedText}
    //                         onChange={(e) => setGeneratedText(e.target.value)}
    //                         className={`w-full p-4 border rounded-md focus:outline-none focus:ring-2 ${
    //                             isGenerating || !generatedText
    //                                 ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
    //                                 : 'focus:ring-blue-500'
    //                         }`}
    //                         rows={18}
    //                         disabled={isGenerating || !generatedText}
    //                     />
    //                 </div>
    //             </div>
    //             <div className="w-1/3 pl-4 border-l-2 border-gray-300">
    //                 <h2 className="text-xl font-semibold mb-4">Feedback</h2>
    //                 <form onSubmit={handleChatSubmit} className="flex gap-2 mb-4">
    //                     <textarea
    //                         value={chatInput}
    //                         onChange={(e) => setChatInput(e.target.value)}
    //                         className={`flex-1 p-2 border rounded-md focus:outline-none focus:ring-2 ${
    //                             isGenerating || !generatedText
    //                                 ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
    //                                 : 'focus:ring-blue-500'
    //                         }`}
    //                         rows={3}
    //                         disabled={isGenerating || !generatedText}
    //                     />
    //                     <button
    //                         type="submit"
    //                         className={`px-4 py-2 rounded-md ${
    //                             isGenerating || !generatedText
    //                                 ? 'bg-blue-400 text-white cursor-not-allowed'
    //                                 : 'bg-blue-600 text-white hover:bg-blue-700'
    //                         }`}
    //                         disabled={isGenerating || !generatedText}
    //                     >
    //                         Regenerate
    //                     </button>
    //                 </form>
    //                 <div className="h-80 overflow-y-auto border p-4 mb-0 rounded-md">
    //                     {chatMessages.map((msg, index) => (
    //                         <div key={index}
    //                              className={`mb-2 ${msg.user === 'User' ? 'text-blue-700' : 'text-gray-700'}`}>
    //                             <strong>{msg.user}:</strong> {msg.message}
    //                         </div>
    //                     ))}
    //                 </div>
    //             </div>
    //         </div>
    //
    //         {/* Save as New Example Button */}
    //         {selectedOption === 'new' && (
    //             <div className="mt-6">
    //                 <button
    //                     onClick={handleSaveNewExample}
    //                     className={`px-4 py-2 rounded-md ${
    //                         isGenerating || !generatedText
    //                             ? 'bg-blue-400 text-white cursor-not-allowed'
    //                             : 'bg-blue-600 text-white hover:bg-blue-700'
    //                     }`}
    //                     disabled={isGenerating || !generatedText}
    //                 >
    //                     Save as New Example
    //                 </button>
    //             </div>
    //         )}
    //
    //         {/* Save Dialog */}
    //         {showSaveDialog && (
    //             <div className="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    //                 <div className="bg-white p-6 rounded-md">
    //                     <h3 className="text-lg font-semibold mb-4">Save New Example</h3>
    //                     <input
    //                         type="text"
    //                         value={newExampleName}
    //                         onChange={(e) => setNewExampleName(e.target.value)}
    //                         className="w-full p-2 mb-4 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    //                         placeholder="Enter new example name"
    //                     />
    //                     <div className="flex justify-end gap-4">
    //                         <button
    //                             onClick={handleSaveDialogClose}
    //                             className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
    //                         >
    //                             Cancel
    //                         </button>
    //                         <button
    //                             onClick={handleSaveDialogSubmit}
    //                             className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
    //                         >
    //                             Save
    //                         </button>
    //                     </div>
    //                 </div>
    //             </div>
    //         )}
    //     </div>
    // );
};

export default Playground;
