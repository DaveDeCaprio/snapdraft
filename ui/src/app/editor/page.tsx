import React, {useEffect, useRef, useState} from 'react';
import {useNavigate, useParams} from 'react-router-dom';
import {documentApi, filesApi} from '@/lib/apiClient.ts';
import DraftCombobox from "@/components/DraftCombobox.tsx";
import Editor from "@/app/editor/Editor.tsx";
import {Draft} from "@/generated/api";

const EditorPage: React.FC = () => {
    const {id, draftId} = useParams() as { id: string; draftId?: string };
    const navigate = useNavigate();

    const [status, setStatus] = useState<string>('Loading...'); // New status indicator
    const [drafts, setDrafts] = useState<Draft[]>([]);
    const [selectedDraft, setSelectedDraft] = useState<{ value: string; label: string } | null>(null);
    const [generatedText, setGeneratedText] = useState<string>('');
    const [chatInput, setChatInput] = useState<string>('');
    const [chatMessages, setChatMessages] = useState<{ user: string; message: string }[]>([]);

    const editorRef = useRef(null);

    useEffect(() => {
        (async () => {
            try {
                const draftsResponse = await documentApi.readAllDrafts(id);
                setDrafts(draftsResponse.data.items);

                if (draftId) {
                    const autoSelectDraft = draftsResponse.data.items.find(d => d.id === draftId);
                    if (autoSelectDraft) {
                        await loadDraft(autoSelectDraft);
                    } else {
                        console.error('Draft not found:', draftId);
                    }
                }
                else {
                    setStatus("Select Draft")
                }
            } catch (error) {
                console.error('Error fetching document data:', error);
            }
        })();
    }, [id, draftId]);

    const loadDraft = async (draft: Draft) => {
        setStatus('Loading...');
        setSelectedDraft({value: draft.id, label: draft.name});

        if (draft.output_file_md_id) {
            // Load output file contents
            try {
                const response = await filesApi.readContents(draft.output_file_md_id);
                setGeneratedText(response.data); // Populate the editor with the file contents
                setStatus('Ready');
            } catch (error) {
                console.error('Error loading file contents:', error);
                setStatus('Error loading file');
            }
        } else {
            // If no output file, generate the document
            setStatus('Generating...');
            try {
                const generateResponse = await documentApi.generateDraft(id, draft.id);
                setGeneratedText(generateResponse.data.text); // Populate the editor
                setStatus('Ready');
            } catch (error) {
                console.error('Error generating document:', error);
                setStatus('Error');
            }
        }

        setChatInput("");
        setChatMessages([]);
    };

    const handleSelectDraft = (draft: { value: string; label: string } | null) => {
        if (draft) {
            const selected = drafts.find((d) => d.id === draft.value);
            if (selected) {
                loadDraft(selected);
            }
        } else {
            setGeneratedText('');
            setStatus('Ready');
        }

        setSelectedDraft(draft);
        navigate(`/doc/${id}/editor/${draft?.value ? draft.value : ''}`);
    };

    const handleChatSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            setStatus("Generating...");

            // Call the regenerate_document API with the current generated text and the chat input
            const regenerateResponse = await documentApi.regenerateDraft(id, draftId!, generatedText, chatInput
            );

            // Update the generated text and chat messages based on the response
            setGeneratedText(regenerateResponse.data.text);
            setChatMessages([
                ...chatMessages,
                {user: 'User', message: chatInput},
                {user: 'System', message: regenerateResponse.data.message}
            ]);
            setChatInput('');
        } catch (error) {
            console.error('Error regenerating document:', error);
        } finally {
            setStatus("Ready");;
        }
    };

    const handleSave = async () => {
        try {
            const draft: Draft = drafts.find((d) => d.id === selectedDraft!.value);
            const fileName = 'generated.md';
            const text = editorRef.current!.getText()
            const file = new File([text], fileName, { type: 'text/markdown' });
            const uploadResponse = await filesApi.uploadFile(file);
            const updatedDraft: Draft = {
                ...draft,
                output_file_id: uploadResponse.data.id,
                // output_file_md_id: uploadResponse.data.id,
            };

            await documentApi.updateDraft(id, draft.id, updatedDraft);
            alert('Draft saved successfully!');
        } catch (error) {
            console.error('Error saving file:', error);
            alert('Failed to save the file.');
        }
    };

    return (
        <div className="flex w-full h-full">
            {/* Left Sidebar */}
            <div className="w-1/4 p-4 bg-gray-100 border-r border-gray-300">
                <div className="mb-6">
                    <div className="flex flex-col md:flex-row gap-4">
                        <div className="flex-1 w-full min-w-0">
                            <DraftCombobox
                                drafts={drafts.map((draft: Draft) => ({
                                    value: draft.id,
                                    label: draft.name,
                                }))}
                                selectedDraft={selectedDraft}
                                setSelectedDraft={handleSelectDraft}
                            />
                        </div>
                        {/* Status Indicator */}
                        <div className="text-center font-semibold text-gray-700  min-w-[100px]">
                            {status}
                        </div>
                    </div>
                </div>
                <h2 className="text-xl font-semibold mb-4">Feedback</h2>
                <form onSubmit={handleChatSubmit} className="mt-4 flex flex-col gap-2">
                     <textarea
                         value={chatInput}
                         onChange={(e) => setChatInput(e.target.value)}
                         className={`w-full p-2 border rounded-md bg-white focus:outline-none focus:ring-2 ${
                             status != "Ready" || !generatedText
                                 ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                                 : 'focus:ring-blue-500'
                         }`}
                         rows={3}
                         disabled={status != "Ready" || !generatedText}
                     />
                    <button
                        type="submit"
                        className={`self-end px-4 py-2 rounded-md ${
                            status != "Ready" || !generatedText
                                ? 'bg-blue-400 text-white cursor-not-allowed'
                                : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                        disabled={status != "Ready" || !generatedText}
                    >
                        Regenerate
                    </button>
                </form>
                <div className="h-80 overflow-y-auto border p-4 mb-0 rounded-md">
                    {chatMessages.map((msg, index) => (
                        <div key={index}
                             className={`mb-2 ${msg.user === 'User' ? 'text-blue-700' : 'text-gray-700'}`}>
                            <strong>{msg.user}:</strong> {msg.message}
                        </div>
                    ))}
                </div>
                <button
                    disabled={status !== "Ready"}
                    onClick={handleSave}
                    className={`mt-4 px-4 py-2 rounded-md ${
                        status === "Ready"
                            ? 'bg-green-600 text-white hover:bg-green-700'
                            : 'bg-gray-400 text-white cursor-not-allowed'
                    }`}
                >
                    Save
                </button>
            </div>

            <div className="flex-1 p-4">
                <Editor ref={editorRef} text={generatedText}/>
            </div>
        </div>
    );
};

export default EditorPage;
