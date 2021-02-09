import { atomFamily, selector, selectorFamily } from "recoil";

import { Range } from "./RangeSlider";
import {
  isBooleanField,
  isLabelField,
  isNumericField,
  isStringField,
} from "./utils";
import * as booleanField from "./BooleanFieldFilter";
import * as numericField from "./NumericFieldFilter";
import * as stringField from "./StringFieldFilter";
import * as atoms from "../../recoil/atoms";
import * as selectors from "../../recoil/selectors";
import { VALID_LIST_TYPES } from "../../utils/labels";
import BooleanFieldFilter from "./BooleanFieldFilter";

export const modalFilterIncludeLabels = atomFamily<string[], string>({
  key: "modalFilterIncludeLabels",
  default: [],
});

export const modalFilterLabelConfidenceRange = atomFamily<Range, string>({
  key: "modalFilterLabelConfidenceRange",
  default: [null, null],
});

export const modalFilterLabelIncludeNoConfidence = atomFamily<boolean, string>({
  key: "modalFilterLabelIncludeNoConfidence",
  default: true,
});

interface Label {
  confidence?: number;
  label?: number;
}

type LabelFilters = {
  [key: string]: (label: Label) => boolean;
};

const getPathExtension = (type) => {
  if (VALID_LIST_TYPES.includes(type)) {
    return ".detections";
  }
  return "";
};

export const labelFilters = selector<LabelFilters>({
  key: "labelFilters",
  get: ({ get }) => {
    const frameLabels = get(atoms.activeLabels("frame"));
    const labels = {
      ...get(atoms.activeLabels("sample")),
      ...Object.keys(frameLabels).reduce((acc, cur) => {
        return {
          ...acc,
          ["frames." + cur]: frameLabels[cur],
        };
      }, {}),
    };
    const filters = {};
    for (const label in labels) {
      const path = `${label}${getPathExtension(label)}`;
      const cRange = get(numericField.rangeAtom(`${path}.confidence`));
      const cNone = get(numericField.noneAtom(`${path}.confidence`));
      const lValues = get(stringField.selectedValuesAtom(`${path}.label`));
      const lNone = get(stringField.noneAtom(`${path}.label`));
      filters[label] = (s) => {
        const inRange =
          cRange[0] - 0.005 <= s.confidence &&
          s.confidence <= cRange[1] + 0.005;
        const noConfidence = cNone && s.confidence === undefined;
        const isIncluded = lValues.length === 0 || lValues.includes(s.label);
        const noLabel = lNone && s.label === undefined;
        return (inRange || noConfidence) && (isIncluded || noLabel);
      };
    }
    return filters;
  },
});

export const modalLabelFilters = selector<LabelFilters>({
  key: "modalLabelFilters",
  get: ({ get }) => {
    const frameLabels = get(atoms.modalActiveLabels("frame"));
    const labels = {
      ...get(atoms.modalActiveLabels("sample")),
      ...Object.keys(frameLabels).reduce((acc, cur) => {
        return {
          ...acc,
          ["frames." + cur]: frameLabels[cur],
        };
      }, {}),
    };
    const hiddenObjects = get(atoms.hiddenObjects);
    const filters = {};
    for (const label in labels) {
      const path = `${label}${getPathExtension(label)}`;
      const range = get(
        atoms.modalFilterLabelConfidenceRange(`${path}.confidence`)
      );
      const none = get(atoms.modalFilterLabelIncludeNoConfidence(label));
      const include = get(atoms.modalFilterIncludeLabels(label));
      filters[label] = (s) => {
        if (hiddenObjects[s.id]) {
          return false;
        }
        const inRange =
          range[0] - 0.005 <= s.confidence && s.confidence <= range[1] + 0.005;
        const noConfidence = none && s.confidence === undefined;
        const isIncluded = include.length === 0 || include.includes(s.label);
        return labels[label] && (inRange || noConfidence) && isIncluded;
      };
    }
    return filters;
  },
  set: ({ get, set }, _) => {
    const paths = get(labelPaths);
    const activeLabels = get(atoms.activeLabels("sample"));
    set(atoms.modalActiveLabels("sample"), activeLabels);
    const activeFrameLabels = get(atoms.activeLabels("frame"));
    set(atoms.modalActiveLabels("frame"), activeFrameLabels);
    for (const label of paths) {
      set(
        modalFilterLabelConfidenceRange(label),
        get(filterLabelConfidenceRange(label))
      );

      set(
        atoms.modalFilterLabelIncludeNoConfidence(label),
        get(filterLabelIncludeNoConfidence(label))
      );

      set(
        atoms.modalFilterIncludeLabels(label),
        get(filterIncludeLabels(label))
      );

      set(atoms.modalColorByLabel, get(atoms.colorByLabel));
    }
  },
});

export const sampleModalFilter = selector({
  key: "sampleModalFilter",
  get: ({ get }) => {
    const filters = get(modalLabelFilters);
    const frameLabels = get(atoms.modalActiveLabels("frame"));
    const activeLabels = {
      ...get(atoms.modalActiveLabels("sample")),
      ...Object.keys(frameLabels).reduce((acc, cur) => {
        return {
          ...acc,
          ["frames." + cur]: frameLabels[cur],
        };
      }, {}),
    };
    return (sample) => {
      return Object.entries(sample).reduce((acc, [key, value]) => {
        if (key === "tags") {
          acc[key] = value;
        } else if (value && VALID_LIST_TYPES.includes(value._cls)) {
          acc[key] =
            filters[key] && value !== null
              ? {
                  ...value,
                  [value._cls.toLowerCase()]: value[
                    value._cls.toLowerCase()
                  ].filter(filters[key]),
                }
              : value;
        } else if (value !== null && filters[key] && filters[key](value)) {
          acc[key] = value;
        } else if (RESERVED_FIELDS.includes(key)) {
          acc[key] = value;
        } else if (
          ["string", "number", "null"].includes(typeof value) &&
          activeLabels[key]
        ) {
          acc[key] = value;
        }
        return acc;
      }, {});
    };
  },
});

export const modalFieldIsFiltered = selectorFamily<boolean, string>({
  key: "modalFieldIsFiltered",
  get: (path) => ({ get }) => {
    const isArgs = { path, modal: true };
    if (get(isBooleanField(path))) {
      return booleanField.fieldIsFiltered(isArgs);
    } else if (get(isNumericField(path))) {
      return numericField.fieldIsFiltered(isArgs);
    } else if (get(isStringField(path))) {
      return stringField.fieldIsFiltered(isArgs);
    }

    path = `${path}${getPathExtension(path)}`;
    const cPath = `${path}.confidence`;
    const lPath = `${path}.label`;

    return (
      get(
        numericField.fieldIsFiltered({
          path: cPath,
          defaultRange: [0, 1],
          modal: true,
        })
      ) || get(stringField.fieldIsFiltered({ path: lPath, modal: true }))
    );
  },
});

export const fieldIsFiltered = selectorFamily<boolean, string>({
  key: "fieldIsFiltered",
  get: (path) => ({ get }) => {
    if (get(isBooleanField(path))) {
      return booleanField.fieldIsFiltered({ path });
    } else if (get(isNumericField(path))) {
      return numericField.fieldIsFiltered({ path });
    } else if (get(isStringField(path))) {
      return stringField.fieldIsFiltered({ path });
    }

    path = `${path}${getPathExtension(path)}`;
    const cPath = `${path}.confidence`;
    const lPath = `${path}.label`;

    return (
      get(
        numericField.fieldIsFiltered({ path: cPath, defaultRange: [0, 1] })
      ) || get(stringField.fieldIsFiltered({ path: lPath }))
    );
  },
});

const meetsDefault = (filter: object, path?: string) => {
  const none = filter.none === true;
  switch (filter._type) {
    case "bool":
      return filter.true === true && filter.false === false && none;
    default:
      throw Error("No Type");
  }
};

const filterDefaults = (filter, path = "") => {
  Object.keys(filter).forEach((key) => {
    if (filter[key]._type && !meetsDefault(filter[key], path)) {
      delete filter[key];
    } else {
      filterDefaults(filter[key], path.length ? `${path}.${key}` : key);
    }
  });
};

export const updateFilter = (filter, path, args) => {
  const keys = path.split(".");
  let o = filter;
  keys.array.forEach((key, idx) => {
    !o[key] && (o[key] = {});
    idx !== keys.length - 1 && (o = o[key]);
    idx === keys.length - 1 && (o[key] = args);
  });

  return filterDefaults(filter);
};

export const GLOBAL_ATOMS = {
  colorByLabel: atoms.colorByLabel,
  includeLabels: selectors.filterIncludeLabels,
  includeNoLabel: selectors.filterIncludeNoLabel,
  includeNoConfidence: selectors.filterLabelIncludeNoConfidence,
  confidenceRange: selectors.filterLabelConfidenceRange,
  confidenceBounds: selectors.labelConfidenceBounds,
  fieldIsFiltered: selectors.fieldIsFiltered,
};

export const MODAL_ATOMS = {
  colorByLabel: atoms.modalColorByLabel,
  includeLabels: atoms.modalFilterIncludeLabels,
  includeNoLabel: selectors.modalFilterIncludeNoLabel,
  includeNoConfidence: atoms.modalFilterLabelIncludeNoConfidence,
  confidenceRange: atoms.modalFilterLabelConfidenceRange,
  confidenceBounds: selectors.labelConfidenceBounds,
  fieldIsFiltered: selectors.modalFieldIsFiltered,
};
