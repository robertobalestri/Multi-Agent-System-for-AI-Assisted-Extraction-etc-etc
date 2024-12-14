import { createIcon } from '@chakra-ui/icons';
import React from 'react';

export const CompareArrowsIcon = createIcon({
  displayName: 'CompareArrows',
  viewBox: '0 0 24 24',
  defaultProps: {
    fill: 'currentColor',
    stroke: 'none',
  },
  path: React.createElement('path', {
    d: 'M9.01 14H2v2h7.01v3L13 15l-3.99-4v3zm5.98-1v-3H22V8h-7.01V5L11 9l3.99 4z',
  }),
}); 