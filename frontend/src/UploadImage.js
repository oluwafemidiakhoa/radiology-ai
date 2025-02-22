import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { analyzeImage } from './api';
import { ClipLoader } from 'react-spinners';

export default function MedicalImagingAnalyzer() {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('');

  // File selection handler
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile?.type.startsWith('image/')) {
      setError('Please upload a valid medical image (JPEG, PNG, or DICOM).');
      return;
    }
    setFile(selectedFile);
    setError('');
    setReport('');
  };

  // AI analysis trigger
  const handleAnalysis = async () => {
    if (!file || !age || !sex) {
      setError('Please provide the image, patient age, and biological sex.');
      return;
    }

    setLoading(true);
    setError('');
    setReport('');

    try {
      // Build FormData
      const formData = new FormData();
      formData.append('file', file);
      formData.append('age', age);
      formData.append('sex', sex);

      // Call backend
      const data = await analyzeImage(formData);
      console.log('Backend response:', data);

      // Backend returns { analysis: "...", filename: "...", etc. }
      if (data?.analysis) {
        setReport(data.analysis);
      } else if (data?.error) {
        setError(data.error);
      } else {
        setError('No analysis text was returned from the server.');
      }
    } catch (err) {
      console.error('Medical image analysis failed:', err);
      setError('Image analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Simple Markdown rendering for the 'analysis' text
  const MedicalReportRenderer = ({ content }) => (
    <ReactMarkdown remarkPlugins={[remarkGfm]}>
      {content}
    </ReactMarkdown>
  );

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-xl shadow-md">
      <h1 className="text-3xl font-bold text-center mb-8 text-blue-600 dark:text-blue-400">
        Medical Imaging Analysis
      </h1>

      <div className="space-y-6">
        {/* File Upload */}
        <div className="space-y-3">
          <label className="block text-lg font-medium text-blue-600 dark:text-blue-400">
            Upload Medical Scan
          </label>
          <input
            type="file"
            onChange={handleFileChange}
            accept="image/*,.dcm"
            className="block w-full file:mr-4 file:py-3 file:px-6 
                       file:border-0 file:rounded-lg 
                       file:bg-blue-600 file:text-white 
                       hover:file:bg-blue-700 
                       dark:file:bg-blue-800 
                       dark:hover:file:bg-blue-900 
                       transition-colors"
          />
        </div>

        {/* Patient Data */}
        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-blue-600 dark:text-blue-400">
              Patient Age
            </label>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value.replace(/\D/g, ''))}
              className="w-full p-3 rounded-lg border 
                         bg-white dark:bg-gray-800 
                         focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Age"
              min="0"
              max="120"
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-blue-600 dark:text-blue-400">
              Biological Sex
            </label>
            <select
              value={sex}
              onChange={(e) => setSex(e.target.value)}
              className="w-full p-3 rounded-lg border 
                         bg-white dark:bg-gray-800 
                         focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>

        {/* Analysis Trigger */}
        <button
          onClick={handleAnalysis}
          disabled={loading}
          className={`w-full py-4 px-8 rounded-lg font-bold text-white transition-colors ${
            loading
              ? 'bg-gray-400'
              : 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-800 dark:hover:bg-blue-900'
          }`}
        >
          {loading ? (
            <div className="flex items-center justify-center gap-2">
              <ClipLoader color="#ffffff" size={24} />
              <span>Analyzing...</span>
            </div>
          ) : (
            'Generate Diagnostic Report'
          )}
        </button>

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-100 rounded-lg text-red-700 dark:text-red-300 border border-red-200 dark:border-red-700">
            {error}
          </div>
        )}

        {/* Analysis Results */}
        {report && !error && (
          <div className="mt-8 p-6 bg-gray-50 dark:bg-gray-700 rounded-xl shadow-md">
            <h2 className="text-2xl font-bold mb-4 text-blue-600 dark:text-blue-400">
              AI Diagnostic Report
            </h2>
            <div className="prose dark:prose-invert max-w-none">
              <MedicalReportRenderer content={report} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
