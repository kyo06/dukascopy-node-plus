export {
  Instrument,
  InstrumentType
} from '../utils/instrument-meta-data/generated/instrument-enum';

// There is 2 GroupData interface be careful this is the good one
import { GroupData } from '../utils/instrument-meta-data/generate-group-data';
import instrumentGroup from '../utils/instrument-meta-data/generated/instrument-groups.json';

const InstrumentGroup = instrumentGroup as GroupData[];

export { InstrumentGroup };
