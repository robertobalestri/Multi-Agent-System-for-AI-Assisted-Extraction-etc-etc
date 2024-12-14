import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  Select,
  Heading,
  Text,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import styles from '@/styles/components/Layout.module.css';
import { NarrativeArcManager } from './components/narrative/NarrativeArcManager';
import { VectorStoreTabManager } from './components/vector/VectorStoreTabManager';
import { CharacterManager } from './components/character/CharacterManager';
import { ApiClient } from './services/api/ApiClient';
import type { NarrativeArc, Episode } from './architecture/types';

const App: React.FC = () => {
  const [series, setSeries] = useState<string[]>([]);
  const [selectedSeries, setSelectedSeries] = useState<string>('');
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [arcs, setArcs] = useState<NarrativeArc[]>([]);
  const api = new ApiClient();

  useEffect(() => {
    const fetchSeries = async () => {
      try {
        const response = await api.request<string[]>('/series');
        if (!response.error) {
          setSeries(response.data);
        }
      } catch (error) {
        console.error('Error fetching series:', error);
        setSeries([]);
      }
    };

    fetchSeries();
  }, []);

  useEffect(() => {
    if (selectedSeries) {
      const fetchData = async () => {
        try {
          const [episodesResponse, arcsResponse] = await Promise.all([
            api.request<Episode[]>(`/episodes/${selectedSeries}`),
            api.request<NarrativeArc[]>(`/arcs/series/${selectedSeries}`)
          ]);

          if (!episodesResponse.error) {
            setEpisodes(episodesResponse.data);
          }
          if (!arcsResponse.error) {
            setArcs(arcsResponse.data);
          }
        } catch (error) {
          console.error('Error fetching data:', error);
          setEpisodes([]);
          setArcs([]);
        }
      };

      fetchData();
    }
  }, [selectedSeries]);

  const handleArcUpdated = async () => {
    if (selectedSeries) {
      try {
        const response = await api.request<NarrativeArc[]>(`/arcs/series/${selectedSeries}`);
        if (!response.error) {
          setArcs(response.data);
        }
      } catch (error) {
        console.error('Error refreshing arcs:', error);
      }
    }
  };

  return (
    <Box className={styles.pageContainer} bg={useColorModeValue('gray.50', 'gray.900')}>
      <Box className={styles.mainContent}>
        <VStack spacing={4} align="stretch">
          <Box className={styles.header} bg={useColorModeValue('white', 'gray.800')}>
            <Heading className={styles.pageTitle}>
              Narrative Arcs Dashboard
            </Heading>
          </Box>

          <Box px={4}>
            <Select
              placeholder="Select series"
              value={selectedSeries}
              onChange={(e) => setSelectedSeries(e.target.value)}
            >
              {series.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </Select>
          </Box>

          {selectedSeries ? (
            <Box className={styles.tabContainer}>
              <Tabs isFitted variant="enclosed">
                <TabList>
                  <Tab>Narrative Arcs</Tab>
                  <Tab>Vector Store</Tab>
                  <Tab>Characters</Tab>
                </TabList>
                <TabPanels>
                  <TabPanel p={0}>
                    <NarrativeArcManager 
                      series={selectedSeries}
                      arcs={arcs}
                      episodes={episodes}
                      onArcUpdated={handleArcUpdated}
                    />
                  </TabPanel>
                  <TabPanel>
                    <VectorStoreTabManager 
                      series={selectedSeries} 
                      onArcUpdated={handleArcUpdated}
                    />
                  </TabPanel>
                  <TabPanel>
                    <CharacterManager 
                      series={selectedSeries} 
                      onCharacterUpdated={handleArcUpdated}
                    />
                  </TabPanel>
                </TabPanels>
              </Tabs>
            </Box>
          ) : (
            <Box textAlign="center" p={8}>
              <Text>Select a series to view the dashboard.</Text>
            </Box>
          )}
        </VStack>
      </Box>
    </Box>
  );
};

export default App;