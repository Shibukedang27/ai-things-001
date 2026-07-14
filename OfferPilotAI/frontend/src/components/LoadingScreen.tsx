export function LoadingScreen() {
  return (
    <div className="loading-screen" aria-live="polite">
      <div className="loading-mark" />
      <div className="loading-stack">
        <div className="loading-line loading-line-lg" />
        <div className="loading-line" />
        <div className="loading-grid">
          <div />
          <div />
          <div />
        </div>
      </div>
    </div>
  );
}
