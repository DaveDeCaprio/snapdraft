import React from 'react';
import { Check, ChevronsUpDown } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from '@/components/ui/command';
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from '@/components/ui/popover';

interface DraftComboboxProps {
    drafts: { value: number; label: string }[];
    selectedDraft: { value: number; label: string } | null;
    setSelectedDraft: (draft: { value: number; label: string } | null) => void;
}

const DraftCombobox: React.FC<DraftComboboxProps> = ({ drafts, selectedDraft, setSelectedDraft }) => {
    const [open, setOpen] = React.useState(false);

    const handleDraftSelect = (currentValue: string) => {
        const selected = drafts.find((draft) => draft.label === currentValue);
        setSelectedDraft(selected ? selected : null);
        setOpen(false);
    };

    return (
        <div className="flex items-center gap-4">
            <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                    <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={open}
                        className="w-full justify-between"
                    >
                        {selectedDraft ? selectedDraft.label : 'Select draft...'}
                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0">
                    <Command>
                        <CommandInput placeholder="Search drafts..." />
                        <CommandList>
                            <CommandEmpty>No draft found.</CommandEmpty>
                            <CommandGroup>
                                {drafts.map((draft) => (
                                    <CommandItem
                                        key={draft.value}
                                        value={draft.label}
                                        onSelect={(currentValue) => handleDraftSelect(currentValue)}
                                    >
                                        <Check
                                            className={cn(
                                                'mr-2 h-4 w-4',
                                                selectedDraft?.value === draft.value ? 'opacity-100' : 'opacity-0'
                                            )}
                                        />
                                        {draft.label}
                                    </CommandItem>
                                ))}
                            </CommandGroup>
                        </CommandList>
                    </Command>
                </PopoverContent>
            </Popover>
        </div>
    );
};

export default DraftCombobox;
