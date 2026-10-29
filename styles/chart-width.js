// Observe only this component's own element, without Streamlit DOM selectors.
export default function ({ parentElement, data, setStateValue }) {
  const probe = parentElement.querySelector(".width-probe");
  let compact = data.compact;
  const observer = new ResizeObserver(([entry]) => {
    const width = entry.contentRect.width;
    if (width <= 0) return;
    const next = width < data.breakpoint;
    if (next !== compact) {
      compact = next;
      setStateValue("compact", next);
    }
  });
  observer.observe(probe);
  return () => observer.disconnect();
}
