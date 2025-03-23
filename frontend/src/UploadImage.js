// src/components/MultiImageViewer.js
import React, { useEffect, useRef } from "react";
import cornerstone from "cornerstone-core";
import cornerstoneTools from "cornerstone-tools";

function MultiImageViewer() {
  const elementRef = useRef(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    // Enable the element for cornerstone
    cornerstone.enable(element);

    // Optional: load a default image if you want
    // e.g. from a local .dcm file or a WADO-RS URL
    // const imageId = 'wadouri:http://localhost:8002/path/to/dicom.dcm';
    // cornerstone.loadImage(imageId).then((image) => {
    //   cornerstone.displayImage(element, image);
    // });

    // Cleanup on unmount
    return () => {
      try {
        cornerstone.disable(element);
      } catch (err) {
        console.error("Error disabling cornerstone element:", err);
      }
    };
  }, []);

  return (
    <div
      ref={elementRef}
      style={{ width: "512px", height: "512px", background: "black", margin: "0 auto" }}
    >
      {/* The Cornerstone canvas will be placed here */}
    </div>
  );
}

export default MultiImageViewer;
