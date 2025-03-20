// src/setupTests.js
import 'jest-canvas-mock';
import { configure } from '@testing-library/react';

configure({ testIdAttribute: 'data-test-id' });