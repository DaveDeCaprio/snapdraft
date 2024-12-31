import React, { useState, useEffect, useRef } from "react";
import { FaEdit, FaTimes } from "react-icons/fa";
import { filesApi } from "@/lib/apiClient.ts";

interface FileEditorProps {
    fileId: string | null; // The current file_id
    onFileIdChange: (newFileId: string | null) => void; // Callback when file_id changes
}

const FileEditor: React.FC<FileEditorProps> = ({ fileId, onFileIdChange }) => {
    const [fileName, setFileName] = useState<string | null>(null);
    const [isEditing, setIsEditing] = useState(false);
    const fileInputRef = useRef<HTMLInputElement | null>(null);

    useEffect(() => {
        const fetchFileName = async () => {
            if (fileId) {
                try {
                    const response = await filesApi.readStoredFile(fileId);
                    setFileName(response.data.metadata.original_filename);
                } catch (error) {
                    console.error("Error fetching file metadata:", error);
                }
            } else {
                setFileName(null);
            }
        };
        fetchFileName();
    }, [fileId]);

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files.length > 0) {
            const file = event.target.files[0];
            try {
                const response = await filesApi.uploadFile(file);
                const newFileId = response.data.id;
                onFileIdChange(newFileId); // Notify parent about the new file_id
                setFileName(file.name); // Update fileName with the uploaded file's name
                setIsEditing(false);
            } catch (error) {
                console.error("Error uploading file:", error);
            }
        }
    };

    const handleClearFile = () => {
        onFileIdChange(null); // Clear the file_id
        setFileName(null); // Reset fileName
        setIsEditing(true); // Immediately show the input box
    };

    const handleEditClick = () => {
        setIsEditing(true);
        if (fileInputRef.current) {
            fileInputRef.current.value = ""; // Clear the file input to allow re-selection
        }
    };

    return (
        <div className="flex items-center gap-2" style={{ minHeight: "40px" }}>
            {isEditing || !fileId ? (
                <>
                    <input
                        type="file"
                        onChange={handleFileChange}
                        ref={fileInputRef}
                        className="p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        style={{ height: "40px" }}
                        title={fileName || "No file selected"} // Show file name as hover text
                    />
                    {fileName && <span className="text-gray-600">{fileName}</span>}
                    {fileId && (
                        <button
                            onClick={() => setIsEditing(false)}
                            className="text-red-600 hover:text-red-800"
                            title="Cancel Edit"
                        >
                            <FaTimes />
                        </button>
                    )}
                </>
            ) : (
                <>
                    <p className="flex items-center gap-2 text-gray-600">
                        {fileName}
                        <button
                            onClick={handleClearFile}
                            className="text-red-600 hover:text-red-800"
                            title="Delete File"
                        >
                            <FaTimes />
                        </button>
                    </p>
                </>
            )}
        </div>
    );
};

export default FileEditor;
