<script>
  let { title, meta = 'Effective date: October 2026', children } = $props();
</script>

<div class="docs-page">
  <div class="docs-container">
    <h1 class="docs-title">{title}</h1>
    <p class="docs-meta">{meta}</p>

    <div class="docs-card">
      {@render children()}
    </div>
  </div>
</div>
