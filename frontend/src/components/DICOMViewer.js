// src/components/DICOMViewer.js
import React, { useEffect, useRef, useState } from "react";
import cornerstone from "cornerstone-core";
import cornerstoneTools from "cornerstone-tools";
import { ClipLoader } from "react-spinners";

export default function DICOMViewer({ imageId }) {
  const viewportRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const element = viewportRef.current;
    if (!element || !imageId) return;

    const loadImage = async () => {
      try {
        setLoading(true);
        cornerstone.enable(element);
        const image = await cornerstone.loadImage(imageId);
        cornerstone.displayImage(element, image);
        // Activate default tools
        cornerstoneTools.setToolActive("Wwwc", {});
        cornerstoneTools.setToolActive("Pan", {});
        setLoading(false);
      } catch (err) {
        setError("Failed to load DICOM image");
        console.error("DICOM load error:", err);
      }
    };

    loadImage();

    return () => {
      if (element) {
        cornerstone.disable(element);
        cornerstoneTools.clearToolState(element);
      }
    };
  }, [imageId]);

  if (error) {
    return (
      <div className="p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded-lg">
        {error}
      </div>
    );
  }

  return (
    <div className="relative h-full w-full">
      {loading && (
        <div className="absolute inset-0 bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
          <ClipLoader size={40} color="#3B82F6" />
        </div>
      )}
      <div
        ref={viewportRef}
        className="h-full w-full bg-black"
        style={{ minWidth: "512px", minHeight: "512px" }}
      />
    </div>
  );
}
