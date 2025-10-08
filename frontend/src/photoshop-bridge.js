/* eslint-disable no-undef */
// Photoshop UXP Bridge
// Provides functions to read active document as PNG bytes and place PNG bytes as a new layer.

let ps, app, batchPlay, fs;
try {
  // UXP environment
  ps = require('photoshop');
  app = ps.app;
  batchPlay = ps.action.batchPlay;
  fs = require('uxp').storage.localFileSystem;
} catch (e) {
  // Non-UXP runtime (e.g., browser preview / dev)
}

function isPhotoshop() {
  return !!(ps && app && batchPlay && fs);
}

async function withProgress(title, fn) {
  if (!isPhotoshop()) return fn();
  return await app.doProgress({ title }, fn);
}

export async function readActiveDocumentAsPNG() {
  if (!isPhotoshop()) {
    console.warn('Photoshop UXP not available; returning null image');
    return null;
  }

  const doc = app.activeDocument;
  if (!doc) return null;

  return await withProgress('Exporting document', async () => {
    const tempFolder = await fs.getTemporaryFolder();
    const tempFile = await tempFolder.createFile('ai-retouch-export.png', { overwrite: true });

    // Use batchPlay to export as PNG to tempFile
    await batchPlay([
      {
        _obj: 'exportSelectionAsFileTypePressed',
        _target: [{ _ref: 'document', _id: doc._id }],
        fileType: 'png',
        quality: 32,
        metadata: 0,
        destFolder: tempFolder.nativePath,
        sRGB: true,
        openWindow: false,
      },
    ], { synchronousExecution: true, modalBehavior: 'fail' });

    const arrayBuffer = await tempFile.read({ format: fs.formats.binary });
    return arrayBuffer; // ArrayBuffer of PNG
  });
}

export async function placeImageFromBytes(bytes, layerName) {
  if (!isPhotoshop()) {
    console.warn('Photoshop UXP not available; skipping place.');
    return false;
  }
  if (!bytes) return false;

  return await withProgress('Placing AI result', async () => {
    const tempFolder = await fs.getTemporaryFolder();
    const tempFile = await tempFolder.createFile('ai-retouch-result.png', { overwrite: true });
    await tempFile.write(bytes, { format: fs.formats.binary });

    // Place as embedded smart object
    await batchPlay([
      {
        _obj: 'placedLayerMake',
        null: {
          _path: tempFile.nativePath,
          _kind: 'local',
        },
        linked: false,
      },
    ], { synchronousExecution: true, modalBehavior: 'fail' });

    // Optionally rename the top layer
    if (layerName) {
      await batchPlay([
        {
          _obj: 'set',
          _target: [{ _ref: 'layer', _enum: 'ordinal', _value: 'targetEnum' }],
          to: { _obj: 'layer', name: String(layerName) },
        },
      ], { synchronousExecution: true, modalBehavior: 'fail' });
    }

    return true;
  });
}

export async function ensureDocument() {
  if (!isPhotoshop()) return true;
  return !!app.activeDocument;
}
