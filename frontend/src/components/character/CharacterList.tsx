import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  IconButton,
  useDisclosure,
  useToast,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Badge,
} from '@chakra-ui/react';
import { EditIcon, DeleteIcon, ChevronDownIcon } from '@chakra-ui/icons';
import { Character } from '@/architecture/types';
import { useApi } from '@/hooks/useApi';
import { ApiClient } from '@/services/api/ApiClient';
import { CharacterEditModal } from './CharacterEditModal';
import { CharacterMergeModal } from './CharacterMergeModal';

interface CharacterListProps {
  series: string;
  characters: Character[];
  onCharacterUpdated: () => void;
}

export const CharacterList: React.FC<CharacterListProps> = ({
  series,
  characters,
  onCharacterUpdated,
}) => {
  const toast = useToast();
  const { request } = useApi();
  const api = new ApiClient();

  // Modals
  const {
    isOpen: isEditModalOpen,
    onOpen: openEditModal,
    onClose: closeEditModal,
  } = useDisclosure();
  const {
    isOpen: isMergeModalOpen,
    onOpen: openMergeModal,
    onClose: closeMergeModal,
  } = useDisclosure();

  // State
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [selectedForMerge, setSelectedForMerge] = useState<Character[]>([]);

  // Handlers
  const handleEdit = (character: Character) => {
    setSelectedCharacter(character);
    openEditModal();
  };

  const handleDelete = async (character: Character) => {
    if (window.confirm(`Are you sure you want to delete ${character.best_appellation}?`)) {
      try {
        await request(() => api.deleteCharacter(series, character.id));
        toast({
          title: 'Character deleted',
          status: 'success',
          duration: 3000,
        });
        onCharacterUpdated();
      } catch (error) {
        toast({
          title: 'Error deleting character',
          description: error instanceof Error ? error.message : 'Unknown error',
          status: 'error',
          duration: 5000,
        });
      }
    }
  };

  const handleMergeSelect = (character: Character) => {
    if (selectedForMerge.length < 2) {
      setSelectedForMerge([...selectedForMerge, character]);
      if (selectedForMerge.length === 1) {
        openMergeModal();
      }
    }
  };

  const handleMergeComplete = async (data: {
    character1_id: string;
    character2_id: string;
    keep_character: 'character1' | 'character2';
  }) => {
    try {
      const mergeData = {
        character1_id: data.character1_id,
        character2_id: data.character2_id,
        keep_character: data.keep_character
      };
      await request(() => api.mergeCharacters(series, mergeData));
      toast({
        title: 'Characters merged successfully',
        status: 'success',
        duration: 3000,
      });
      setSelectedForMerge([]);
      closeMergeModal();
      onCharacterUpdated();
    } catch (error) {
      toast({
        title: 'Error merging characters',
        description: error instanceof Error ? error.message : 'Unknown error',
        status: 'error',
        duration: 5000,
      });
    }
  };

  return (
    <VStack spacing={4} align="stretch">
      {characters.map((character) => (
        <Box
          key={character.id}
          p={4}
          borderWidth={1}
          borderRadius="md"
          position="relative"
        >
          <HStack justify="space-between">
            <VStack align="start" spacing={1}>
              <Text fontWeight="bold">{character.best_appellation}</Text>
              <HStack>
                {character.appellations.map((appellation) => (
                  <Badge key={appellation} colorScheme="blue">
                    {appellation}
                  </Badge>
                ))}
              </HStack>
            </VStack>
            <HStack>
              <IconButton
                aria-label="Edit character"
                icon={<EditIcon />}
                size="sm"
                onClick={() => handleEdit(character)}
              />
              <IconButton
                aria-label="Delete character"
                icon={<DeleteIcon />}
                size="sm"
                colorScheme="red"
                onClick={() => handleDelete(character)}
              />
              <Menu>
                <MenuButton
                  as={Button}
                  rightIcon={<ChevronDownIcon />}
                  size="sm"
                  isDisabled={selectedForMerge.includes(character)}
                >
                  Merge
                </MenuButton>
                <MenuList>
                  <MenuItem onClick={() => handleMergeSelect(character)}>
                    Select for merge ({selectedForMerge.length}/2)
                  </MenuItem>
                </MenuList>
              </Menu>
            </HStack>
          </HStack>
        </Box>
      ))}

      {/* Modals */}
      {selectedCharacter && (
        <CharacterEditModal
          isOpen={isEditModalOpen}
          onClose={closeEditModal}
          character={selectedCharacter}
          onSave={async (data) => {
            try {
              await request(() => api.updateCharacter(series, data));
              toast({
                title: 'Character updated',
                status: 'success',
                duration: 3000,
              });
              closeEditModal();
              onCharacterUpdated();
            } catch (error) {
              toast({
                title: 'Error updating character',
                description: error instanceof Error ? error.message : 'Unknown error',
                status: 'error',
                duration: 5000,
              });
            }
          }}
        />
      )}

      {selectedForMerge.length === 2 && (
        <CharacterMergeModal
          isOpen={isMergeModalOpen}
          onClose={() => {
            closeMergeModal();
            setSelectedForMerge([]);
          }}
          character1={selectedForMerge[0]}
          character2={selectedForMerge[1]}
          onMergeComplete={handleMergeComplete}
        />
      )}
    </VStack>
  );
}; 