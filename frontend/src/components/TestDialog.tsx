import { Dialog } from "@chakra-ui/react";

interface TestDialogProps {
    isOpen: boolean;
    onClose: () => void;
}

export const TestDialog = ({ isOpen, onClose }: TestDialogProps) => {
    return (
        <Dialog.Root open={isOpen} onOpenChange={(e) => !e.open && onClose()}>
            <Dialog.Backdrop />
            <Dialog.Positioner>
                <Dialog.Content>
                    <Dialog.Header>
                        <Dialog.Title>Test Dialog</Dialog.Title>
                    </Dialog.Header>
                    <Dialog.CloseTrigger />
                    <Dialog.Body>
                        <p>
                            This is a test dialog. If you see this, the dialog
                            is working!
                        </p>
                    </Dialog.Body>
                </Dialog.Content>
            </Dialog.Positioner>
        </Dialog.Root>
    );
};
