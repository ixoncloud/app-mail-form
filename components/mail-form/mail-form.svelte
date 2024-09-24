<script lang="ts">
  import type { ComponentContext, BackendComponentClient } from '@ixon-cdk/types';
  import { onMount } from 'svelte';

  export let context: ComponentContext;

  let rootEl: HTMLDivElement;
  let height: number | null = null;
  let client: BackendComponentClient;
  let loading = false;
  let disabled = false;
  let emailMessage = '';
  let subject = '';

  $: hasHeader = header && (header.title || header.subtitle) && !isShallow;
  $: isShallow = height !== null ? height <= 60 : false;
  $: header = context ? context.inputs.header : undefined;

  onMount(() => {
    if (context.mode === 'edit') {
      disabled = true;
    }

    client = context.createBackendComponentClient();
    subject = context.inputs.subject;

    const resizeObserver = new ResizeObserver(entries => {
      entries.forEach(entry => {
        height = entry.contentRect.height;
      });
    });
    resizeObserver.observe(rootEl);

    return () => {
      resizeObserver.unobserve(rootEl);
      client.destroy();
    };
  });

  async function openEmailDialog() {
    const result = await context.openFormDialog({
      title: subject,
      inputs: [
        {
          key: 'message',
          type: 'Text',
          label: 'Enter your message',
          required: true,
          translate: false,
        },
      ],
      submitButtonText: 'Send Message',
    });

    if (result) {
      emailMessage = result.value.message;
      await sendEmail();
    }
  }

  async function sendEmail() {
    loading = true;
    try {
      const response = await client.call('send_email', {
        subject: subject,
        message: emailMessage,
      });
      if (response.data.status === 'success') {
        await context.openAlertDialog({
          title: 'Success',
          message: 'Your message has been sent successfully.',
        });
      } else {
        throw new Error(response.data.message || 'Failed to send message.');
      }
    } catch (error: Error | any) {
      await context.openAlertDialog({
        title: 'Error',
        message:
          error.message || 'An error occurred while sending your message.',
      });
    } finally {
      loading = false;
    }
  }
</script>

<div class="card" bind:this={rootEl}>
  {#if hasHeader}
    <div class="card-header">
      {#if header.title}
        <h3 class="card-title">{header.title}</h3>
      {/if}
      {#if header.subtitle}
        <h4 class="card-subtitle">{header.subtitle}</h4>
      {/if}
    </div>
  {/if}
  <div class="card-content justify-center">
    {#if !loading}
      <button
        class="button primary {isShallow ? ' small-button' : ''}"
        on:click|stopPropagation={openEmailDialog}
        disabled={loading || disabled}>{subject}</button
      >
    {:else}
      <p>Sending...</p>
    {/if}
  </div>
</div>

<style lang="scss">
  @import './styles/card';
  @import './styles/button';

  button {
    width: 100%;
    max-height: 36px;
  }

  .justify-center {
    display: flex;
    justify-content: center;
  }

  .small-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-top: -4px;
  }
</style>
