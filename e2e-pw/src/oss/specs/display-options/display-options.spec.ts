import { test as base } from "src/oss/fixtures";
import { GridActionsRowPom } from "src/oss/poms/action-row/grid-actions-row";
import { PanelPom } from "src/oss/poms/panel";
import { getUniqueDatasetNameWithPrefix } from "src/oss/utils";

const test = base.extend<{
  actionsRow: GridActionsRowPom;
  panel: PanelPom;
}>({
  actionsRow: async ({ page }, use) => {
    await use(new GridActionsRowPom(page));
  },
  panel: async ({ page }, use) => {
    await use(new PanelPom(page));
  },
});

test.describe("Display Options", () => {
  const datasetName = getUniqueDatasetNameWithPrefix("quickstart-groups");

  test.beforeAll(async ({ fiftyoneLoader }) => {
    await fiftyoneLoader.loadZooDataset("quickstart-groups", datasetName, {
      max_samples: 12,
    });
  });

  test.beforeEach(async ({ page, fiftyoneLoader }) => {
    await fiftyoneLoader.waitUntilGridVisible(page, datasetName);
  });

  test("switching display options statistics to group should be successful when histogram is open", async ({
    actionsRow,
    panel,
  }) => {
    await panel.open("Histograms");
    await panel.bringPanelToForeground("Samples");
    await actionsRow.toggleDisplayOptions();
    await actionsRow.displayActions.setSidebarStatisticsMode("group");
    await actionsRow.toggleDisplayOptions();
    await panel.bringPanelToForeground("Histograms");

    await panel.histogramDistributionContainer.waitFor({ state: "visible" });
    await panel.histogramDistributionContainer.click();

    await panel.assert.isHistogramLoaded();
  });
});
