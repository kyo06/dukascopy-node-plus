/* eslint-disable no-console */
import path from 'path';
import fs from 'fs';
import { promisify } from 'util';
import { wait } from '../general';
import { DATA_API_ROOT } from '../../config/data-api';
import { generateInstrumentGroupData } from './generate-group-data';
import { generateMeta } from './generate-meta';
import { generateInstrumentEnum } from './generate-instrument-enum';
import { generateInstrumentMarkdown } from './generate-instrument-md';
import { ApiInstrumentDetail, InstrumentsResponse } from './generate-data.types';

const saveFile = promisify(fs.writeFile);
const OUTPUT_FOLDER = path.resolve(__dirname, 'generated');
const DETAIL_REQUEST_PAUSE_MS = 250;
const RETRY_DELAYS_MS = [1000, 2000, 4000, 8000, 16000];
const MAX_RETRY_AFTER_MS = 30_000;

class ApiRequestError extends Error {
  retryable: boolean;
  retryAfterMs: number | null;

  constructor(message: string, retryable: boolean, retryAfterMs: number | null = null) {
    super(message);
    this.retryable = retryable;
    this.retryAfterMs = retryAfterMs;
  }
}

function parseRetryAfterMs(response: Response): number | null {
  const header = response.headers.get('retry-after');

  if (!header) {
    return null;
  }

  const seconds = Number(header);

  if (Number.isFinite(seconds)) {
    return Math.min(seconds * 1000, MAX_RETRY_AFTER_MS);
  }

  const dateMs = Date.parse(header);

  return Number.isFinite(dateMs) ? Math.min(Math.max(dateMs - Date.now(), 0), MAX_RETRY_AFTER_MS) : null;
}

async function fetchJsonWithRetry<T>(url: string): Promise<T> {
  let lastError: unknown;

  for (let attempt = 0; attempt <= RETRY_DELAYS_MS.length; attempt++) {
    try {
      const response = await fetch(url);

      if (!response.ok) {
        const isTransient =
          response.status === 408 || response.status === 429 || response.status >= 500;
        throw new ApiRequestError(
          `Request failed with status ${response.status}: ${url}`,
          isTransient,
          response.status === 429 ? parseRetryAfterMs(response) : null
        );
      }

      return (await response.json()) as T;
    } catch (error) {
      lastError = error;

      if (error instanceof ApiRequestError && !error.retryable) {
        throw error;
      }

      if (attempt < RETRY_DELAYS_MS.length) {
        const delayMs =
          error instanceof ApiRequestError && error.retryAfterMs !== null
            ? error.retryAfterMs
            : RETRY_DELAYS_MS[attempt];
        await wait(delayMs);
      }
    }
  }

  throw lastError;
}

async function getInstrumentDetails(metadata: InstrumentsResponse): Promise<ApiInstrumentDetail[]> {
  const details: ApiInstrumentDetail[] = [];

  for (let index = 0; index < metadata.instruments.length; index++) {
    const instrument = metadata.instruments[index];
    console.log(`[${index + 1}/${metadata.instruments.length}] ${instrument.code}`);
    details.push(
      await fetchJsonWithRetry<ApiInstrumentDetail>(
        `${DATA_API_ROOT}/instruments/${encodeURIComponent(instrument.code)}`
      )
    );

    if (index < metadata.instruments.length - 1) {
      await wait(DETAIL_REQUEST_PAUSE_MS);
    }
  }

  return details;
}

async function run(): Promise<void> {
  const metadata = await fetchJsonWithRetry<InstrumentsResponse>(`${DATA_API_ROOT}/instruments`);
  const instrumentDetails = await getInstrumentDetails(metadata);
  const artifactNames = [
    `raw-meta-data-${new Date().toISOString().slice(0, 10)}.json`,
    'instrument-meta-data.json',
    'instrument-enum.ts',
    'instrument-groups.json',
    'instruments.md'
  ] as const;
  const generatedParentFolder = path.dirname(OUTPUT_FOLDER);
  const generationId = `${process.pid}-${Date.now()}`;
  const stagingFolder = path.resolve(generatedParentFolder, `.generated-staging-${generationId}`);
  const backupFolder = path.resolve(generatedParentFolder, `.generated-backup-${generationId}`);
  const [rawName, metadataName, enumName, groupsName, documentationName] = artifactNames;
  const rawMetadataPath = path.resolve(stagingFolder, rawName);
  const metadataPath = path.resolve(stagingFolder, metadataName);
  const enumPath = path.resolve(stagingFolder, enumName);
  const groupsPath = path.resolve(stagingFolder, groupsName);
  const documentationPath = path.resolve(stagingFolder, documentationName);

  await fs.promises.mkdir(stagingFolder, { recursive: true });

  try {
    await saveFile(rawMetadataPath, JSON.stringify(metadata, null, 2));
    await generateMeta(instrumentDetails, metadataPath);
    await generateInstrumentEnum(metadataPath, enumPath);
    await generateInstrumentGroupData(metadata, groupsPath);
    await generateInstrumentMarkdown({
      groupsPath,
      metadataPath,
      outputPath: documentationPath
    });

    await Promise.all(
      artifactNames.map(name => fs.promises.access(path.resolve(stagingFolder, name)))
    );

    await fs.promises.rename(OUTPUT_FOLDER, backupFolder);

    try {
      await fs.promises.rename(stagingFolder, OUTPUT_FOLDER);
    } catch (error) {
      await fs.promises.rename(backupFolder, OUTPUT_FOLDER);
      throw error;
    }

    await fs.promises.rm(backupFolder, { recursive: true, force: true });
    console.log('Done');
  } finally {
    await fs.promises.rm(stagingFolder, { recursive: true, force: true });
  }
}

if (require.main === module) {
  run().catch(error => {
    console.error(error);
    process.exitCode = 1;
  });
}

export { fetchJsonWithRetry, getInstrumentDetails, run };
