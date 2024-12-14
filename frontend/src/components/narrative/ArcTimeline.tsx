import React from 'react';
import {
  Box,
  Grid,
  Text,
  VStack,
  HStack,
  Button,
  Badge,
  useColorModeValue,
} from '@chakra-ui/react';
import type { NarrativeArc, ArcProgression } from '@/architecture/types';
import styles from '@/styles/components/ArcTimeline.module.css';
import { StarIcon } from '@chakra-ui/icons';

interface ArcTimelineProps {
  arcs: NarrativeArc[];
  episodes: { season: string; episode: string; }[];
  selectedSeason: string;
  selectedEpisode: string;
  onCellClick: (arc: NarrativeArc, season: string, episode: string) => void;
  isMergeMode: boolean;
  selectedForMerge: NarrativeArc[];
  onToggleMerge: (arc: NarrativeArc) => void;
  onEditArc: (arc: NarrativeArc) => void;
  onGenerateAll: (arc: NarrativeArc, overwriteExisting?: boolean) => void;
}

export const ArcTimeline: React.FC<ArcTimelineProps> = ({
  arcs,
  episodes,
  selectedSeason,
  selectedEpisode,
  onCellClick,
  isMergeMode,
  selectedForMerge,
  onToggleMerge,
  onEditArc,
  onGenerateAll,
}) => {
  const bgColor = useColorModeValue('gray.50', 'gray.700');
  const cellBgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const seasonEpisodes = React.useMemo(() => {
    const filteredEpisodes = episodes
      .filter(ep => ep.season === selectedSeason)
      .sort((a, b) => parseInt(a.episode.replace('E', '')) - parseInt(b.episode.replace('E', '')));

    if (selectedEpisode) {
      return filteredEpisodes.filter(ep => ep.episode === selectedEpisode);
    }

    return filteredEpisodes;
  }, [episodes, selectedSeason, selectedEpisode]);

  const getArcTypeColor = (arcType: string): string => {
    const typeColors = {
      'Soap Arc': '#F687B3',
      'Genre-Specific Arc': '#ED8936',
      'Anthology Arc': '#48BB78',
    };
    return typeColors[arcType as keyof typeof typeColors] || '#A0AEC0';
  };

  return (
    <Box className={styles.timelineContainer}>
      <Grid
        templateColumns={`300px repeat(${seasonEpisodes.length}, minmax(200px, 1fr))`}
        className={styles.timelineGrid}
        bg={bgColor}
      >
        <Box 
          className={styles.stickyHeader}
          borderColor={borderColor}
          bg={cellBgColor}
        >
          <Text fontWeight="bold">Arc Details</Text>
        </Box>
        
        {seasonEpisodes.map(ep => (
          <Box 
            key={`header-${ep.episode}`} 
            className={styles.headerCell}
            borderColor={borderColor}
            bg={cellBgColor}
          >
            <VStack spacing={1}>
              <Text fontWeight="bold">
                Season {selectedSeason.replace('S', '')}
              </Text>
              <Text>
                Episode {ep.episode.replace('E', '')}
              </Text>
            </VStack>
          </Box>
        ))}

        {arcs.map(arc => (
          <React.Fragment key={arc.id}>
            <Box
              className={styles.arcTitleCell}
              borderColor={borderColor}
              bg={cellBgColor}
            >
              <VStack align="stretch" spacing={3}>
                <HStack justify="space-between" align="flex-start">
                  <VStack align="start" spacing={2} flex={1}>
                    <div className={styles.arcTitleBox}>
                      {arc.title}
                    </div>
                    <Text fontSize="sm" color="gray.600">
                      {arc.main_characters.join(', ')}
                    </Text>
                  </VStack>
                  <VStack align="end" spacing={2}>
                    <Badge 
                      colorScheme={getArcTypeColor(arc.arc_type).replace('#', '')} 
                      fontSize="xs"
                      bg={getArcTypeColor(arc.arc_type)}
                      color="white"
                    >
                      {arc.arc_type}
                    </Badge>
                    <Button
                      size="sm"
                      colorScheme="blue"
                      onClick={(e) => {
                        e.stopPropagation();
                        onEditArc(arc);
                      }}
                    >
                      Edit
                    </Button>
                    <Button
                      size="sm"
                      colorScheme="purple"
                      leftIcon={<StarIcon />}
                      onClick={(e) => {
                        e.stopPropagation();
                        onGenerateAll(arc);
                      }}
                    >
                      Generate All
                    </Button>
                  </VStack>
                </HStack>
                {isMergeMode && (
                  <Button
                    size="xs"
                    colorScheme={selectedForMerge.includes(arc) ? "red" : "blue"}
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleMerge(arc);
                    }}
                  >
                    {selectedForMerge.includes(arc) ? "Deselect" : "Select"}
                  </Button>
                )}
              </VStack>
            </Box>

            {seasonEpisodes.map(ep => {
              const prog = arc.progressions.find(
                (p: ArcProgression) => p.season === ep.season && p.episode === ep.episode
              );
              return (
                <Box
                  key={`${arc.id}-${ep.episode}`}
                  className={styles.timelineCell}
                  onClick={() => onCellClick(arc, ep.season, ep.episode)}
                  style={{
                    border: prog ? `2px solid ${getArcTypeColor(arc.arc_type)}` : '1px dashed gray',
                    background: cellBgColor
                  }}
                >
                  {prog && (
                    <VStack align="stretch" spacing={2}>
                      <Text fontSize="sm" noOfLines={3}>
                        {prog.content}
                      </Text>
                      {prog.interfering_characters && prog.interfering_characters.length > 0 && (
                        <Text fontSize="xs" color="gray.500" mt={2}>
                          <Text as="span" fontWeight="bold">Interfering: </Text>
                          {prog.interfering_characters.join(', ')}
                        </Text>
                      )}
                    </VStack>
                  )}
                </Box>
              );
            })}
          </React.Fragment>
        ))}
      </Grid>
    </Box>
  );
};