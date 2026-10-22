<script>
  import LeftPanel from '../components/LeftPanel.svelte';
  import LifetimePicker from '../components/compose/LifetimePicker.svelte';
  import SecretTextarea from '../components/compose/SecretTextarea.svelte';
  import SuccessCard from '../components/compose/SuccessCard.svelte';
  import QuotaModal from '../components/compose/QuotaModal.svelte';
  import { useQuota } from '../composables/useQuota.svelte.js';
  import { createSecret, recordLocalSecretGeneration, pickStricterQuota } from '../lib/api.js';
  import { encryptSecretClient } from '../lib/crypto.js';
  import LoaderCircle from '@lucide/svelte/icons/loader-circle';
  import Link from '@lucide/svelte/icons/link';

  const quota = useQuota();

  let textInput = $state('');
  let lifetime = $state(3600);
  let shakeInput = $state(false);
  let isGenerating = $state(false);
  let generatedUrl = $state('');
  let showQuotaModal = $state(false);
  let errorMessage = $state('');

  function shake() {
    shakeInput = true;
    setTimeout(() => { shakeInput = false; }, 700);
  }

  function finalizeGeneratedSecret(secretId, keyB64, nextQuota) {
    quota.set(nextQuota);
    const fragment = keyB64 ? `#${keyB64}` : '';
    generatedUrl = `${window.location.origin}/accept?s=${secretId}${fragment}`;
    textInput = '';
  }

  async function handleGenerate() {
    const trimmed = textInput.trim();
    if (!trimmed) {
      shake();
      return;
    }

    errorMessage = '';
    await quota.refresh();
    if (quota.value.remaining <= 0) {
      showQuotaModal = true;
      return;
    }

    isGenerating = true;

    try {
      const { payload, key } = await encryptSecretClient(trimmed);
      const result = await createSecret({ text: payload, lifetime });
      const nextQuota = pickStricterQuota(result?.quota, recordLocalSecretGeneration());
      finalizeGeneratedSecret(result.id, key, nextQuota);
    } catch (err) {
      if (err?.status === 429) {
        quota.exhaust(err.quota);
        showQuotaModal = true;
        return;
      }

      console.error(err);
      errorMessage = err?.message || 'Failed to generate secret link. Please try again.';
      shake();
    } finally {
      isGenerating = false;
    }
  }
</script>

<div class="page compose-page">
  <LeftPanel />

  <div class="right-panel">
    {#if !generatedUrl}
      <div class="compose-header-bar">
        <div class="compose-title-group">
          <h2 class="compose-title">
            New <span class="accent">secret</span>
          </h2>
          <p class="compose-sub">Type your confidential message</p>
        </div>

        <LifetimePicker bind:value={lifetime} />
      </div>

      <SecretTextarea bind:value={textInput} shake={shakeInput} />

      {#if errorMessage}
        <p class="compose-error-msg">{errorMessage}</p>
      {/if}

      <div class="generate-action-group">
        <button
          class="btn-generate"
          onclick={handleGenerate}
          disabled={isGenerating}
        >
          {#if isGenerating}
            <LoaderCircle size={16} strokeWidth={2.5} class="spin-icon" />
            <span>Generating link…</span>
          {:else}
            <Link size={17} strokeWidth={2.5} />
            <span>Generate link</span>
          {/if}
        </button>
      </div>

      <p class="privacy-note">Encrypted on your device. We can’t read your message.</p>
    {:else}
      <SuccessCard url={generatedUrl} />
    {/if}
  </div>
</div>

{#if showQuotaModal}
  <QuotaModal resetInSeconds={quota.value.reset_in_seconds} onclose={() => { showQuotaModal = false; }} />
{/if}
