import {useState, useEffect, useRef, useMemo, forwardRef, useImperativeHandle} from 'react';
import { CKEditor } from '@ckeditor/ckeditor5-react';
import {
    DecoupledEditor,
    Alignment,
    Autoformat,
    AutoLink,
    Autosave,
    BalloonToolbar,
    BlockQuote,
    Bold,
    Code,
    Essentials,
    FontBackgroundColor,
    FontColor,
    FontFamily,
    FontSize,
    GeneralHtmlSupport,
    Heading,
    Highlight,
    HorizontalLine,
    Indent,
    IndentBlock,
    Italic,
    Link,
    List,
    ListProperties,
    Markdown,
    Minimap,
    Paragraph,
    PasteFromMarkdownExperimental,
    PasteFromOffice,
    RemoveFormat,
    SpecialCharacters,
    SpecialCharactersArrows,
    SpecialCharactersCurrency,
    SpecialCharactersEssentials,
    SpecialCharactersLatin,
    SpecialCharactersMathematical,
    SpecialCharactersText,
    Strikethrough,
    Subscript,
    Superscript,
    Table,
    TableCaption,
    TableCellProperties,
    TableColumnResize,
    TableProperties,
    TableToolbar,
    TextTransformation,
    Underline
} from 'ckeditor5';

import 'ckeditor5/ckeditor5.css';

import './Editor.css';

interface EditorProps {
    text: string;
    // onTextChange?: (newText: string) => void; // Optional prop
}

const Editor: React.FC<EditorProps> = forwardRef(({ text }, ref) => {

    const editorContainerRef = useRef(null);
    const editorMenuBarRef = useRef(null);
    const editorToolbarRef = useRef(null);
    const editorRef = useRef(null);
    const editorInstanceRef = useRef(null);
    const editorMinimapRef = useRef(null);
    const [isLayoutReady, setIsLayoutReady] = useState(false);

    useEffect(() => {
        setIsLayoutReady(true);

        return () => setIsLayoutReady(false);
    }, []);

    useImperativeHandle(ref, () => ({
        getText: () => {
            console.log("Editor", editorInstanceRef.current)
            const text = editorInstanceRef.current!.getData()
            console.log("Text", text)
            return text;
        }
    }));

    const { editorConfig } = useMemo(() => {
        if (!isLayoutReady) {
            return {};
        }

        return {
            editorConfig: {
                toolbar: {
                    items: [
                        'heading',
                        '|',
                        'fontSize',
                        'fontFamily',
                        'fontColor',
                        'fontBackgroundColor',
                        '|',
                        'bold',
                        'italic',
                        'underline',
                        '|',
                        'link',
                        'insertTable',
                        'highlight',
                        'blockQuote',
                        '|',
                        'alignment',
                        '|',
                        'bulletedList',
                        'numberedList',
                        'outdent',
                        'indent'
                    ],
                    shouldNotGroupWhenFull: false
                },
                plugins: [
                    Alignment,
                    Autoformat,
                    AutoLink,
                    Autosave,
                    BalloonToolbar,
                    BlockQuote,
                    Bold,
                    Code,
                    Essentials,
                    FontBackgroundColor,
                    FontColor,
                    FontFamily,
                    FontSize,
                    GeneralHtmlSupport,
                    Heading,
                    Highlight,
                    HorizontalLine,
                    Indent,
                    IndentBlock,
                    Italic,
                    Link,
                    List,
                    ListProperties,
                    Markdown,
                    Minimap,
                    Paragraph,
                    PasteFromMarkdownExperimental,
                    PasteFromOffice,
                    RemoveFormat,
                    SpecialCharacters,
                    SpecialCharactersArrows,
                    SpecialCharactersCurrency,
                    SpecialCharactersEssentials,
                    SpecialCharactersLatin,
                    SpecialCharactersMathematical,
                    SpecialCharactersText,
                    Strikethrough,
                    Subscript,
                    Superscript,
                    Table,
                    TableCaption,
                    TableCellProperties,
                    TableColumnResize,
                    TableProperties,
                    TableToolbar,
                    TextTransformation,
                    Underline
                ],
                balloonToolbar: ['bold', 'italic', '|', 'link', '|', 'bulletedList', 'numberedList'],
                fontFamily: {
                    supportAllValues: true
                },
                fontSize: {
                    options: [10, 12, 14, 'default', 18, 20, 22],
                    supportAllValues: true
                },
                heading: {
                    options: [
                        {
                            model: 'paragraph',
                            title: 'Paragraph',
                            class: 'ck-heading_paragraph'
                        },
                        {
                            model: 'heading1',
                            view: 'h1',
                            title: 'Heading 1',
                            class: 'ck-heading_heading1'
                        },
                        {
                            model: 'heading2',
                            view: 'h2',
                            title: 'Heading 2',
                            class: 'ck-heading_heading2'
                        },
                        {
                            model: 'heading3',
                            view: 'h3',
                            title: 'Heading 3',
                            class: 'ck-heading_heading3'
                        },
                        {
                            model: 'heading4',
                            view: 'h4',
                            title: 'Heading 4',
                            class: 'ck-heading_heading4'
                        },
                        {
                            model: 'heading5',
                            view: 'h5',
                            title: 'Heading 5',
                            class: 'ck-heading_heading5'
                        },
                        {
                            model: 'heading6',
                            view: 'h6',
                            title: 'Heading 6',
                            class: 'ck-heading_heading6'
                        }
                    ]
                },
                htmlSupport: {
                    allow: [
                        {
                            name: /^.*$/,
                            styles: true,
                            attributes: true,
                            classes: true
                        }
                    ]
                },
                initialData: '',
                licenseKey: "GPL",
                link: {
                    addTargetToExternalLinks: true,
                    defaultProtocol: 'https://',
                    decorators: {
                        toggleDownloadable: {
                            mode: 'manual',
                            label: 'Downloadable',
                            attributes: {
                                download: 'file'
                            }
                        }
                    }
                },
                list: {
                    properties: {
                        styles: true,
                        startIndex: true,
                        reversed: true
                    }
                },
                menuBar: {
                    isVisible: true
                },
                minimap: {
                    container: editorMinimapRef.current,
                    extraClasses: 'editor-container_include-minimap ck-minimap__iframe-content'
                },
                placeholder: 'Type or paste your content here!',
                table: {
                    contentToolbar: ['tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties']
                }
            }
        };
    }, [isLayoutReady]);

    return (
        <div className="editor-parent">
            <div className="editor-container editor-container_document-editor editor-container_include-minimap" ref={editorContainerRef}>
                <div className="editor-container__menu-bar" ref={editorMenuBarRef}></div>
                <div className="editor-container__toolbar" ref={editorToolbarRef}></div>
                <div className="editor-container__minimap-wrapper">
                    <div className="editor-container__editor-wrapper">
                        <div className="editor-container__editor">
                            <div ref={editorRef}>
                                {editorConfig && (
                                    <CKEditor
                                        onReady={editor => {
                                            editorInstanceRef.current = editor;
                                            editorToolbarRef.current.appendChild(editor.ui.view.toolbar.element);
                                            editorMenuBarRef.current.appendChild(editor.ui.view.menuBarView.element);
                                        }}
                                        onAfterDestroy={() => {
                                            Array.from(editorToolbarRef.current.children).forEach(child => child.remove());
                                            Array.from(editorMenuBarRef.current.children).forEach(child => child.remove());
                                        }}
                                        onChange={(event, editor) => {
                                            editorInstanceRef.current = editor;
                                        }}
                                        editor={DecoupledEditor}
                                        config={editorConfig}
                                        data={text}
                                    />
                                )}
                            </div>
                        </div>
                    </div>
                    <div className="editor-container__sidebar editor-container__sidebar_minimap">
                        <div ref={editorMinimapRef}></div>
                    </div>
                </div>
            </div>
        </div>
    );
});

export default Editor;