import { getFetchOrigin, getFetchPathPrefix } from "@fiftyone/utilities";

export const getSampleSrc = (url: string) => {
  // Ingedata custom code to return full url correctly
  // console.log(url);
  const newUrl = url.replace(/^\/.*https?:\//, "https://");
  // console.log(newUrl);

  return newUrl;

  try {
    const { protocol } = new URL(url);
    if (["http:", "https:"].includes(protocol)) {
      return url;
    }
  } catch {}

  return `${getFetchOrigin()}${getFetchPathPrefix()}/media?filepath=${encodeURIComponent(
    url
  )}`;
};
