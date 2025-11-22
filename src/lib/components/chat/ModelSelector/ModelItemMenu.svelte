<script lang="ts">
	import { DropdownMenu } from 'bits-ui';
	import { flyAndScale } from '$lib/utils/transitions';

	import { getContext } from 'svelte';
	import { goto } from '$app/navigation';

	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Link from '$lib/components/icons/Link.svelte';
	import Eye from '$lib/components/icons/Eye.svelte';
	import EyeSlash from '$lib/components/icons/EyeSlash.svelte';
	import { settings } from '$lib/stores';

	const i18n = getContext('i18n');

	export let show = false;
	export let model;

	export let pinModelHandler: (modelId: string) => void = () => {};
	export let copyLinkHandler: Function = () => {};

	export let onClose: Function = () => {};
</script>

<DropdownMenu.Root
	bind:open={show}
	closeFocus={false}
	onOpenChange={(state) => {
		if (state === false) {
			onClose();
		}
	}}
	typeahead={false}
>
	<DropdownMenu.Trigger>
		<Tooltip
			content={$i18n.t('More')}
			className={($settings?.highContrastMode ?? false)
				? ''
				: 'group-hover/item:opacity-100 opacity-0'}
		>
			<slot />
		</Tooltip>
	</DropdownMenu.Trigger>

	<DropdownMenu.Content
		strategy="fixed"
		class="w-full max-w-[180px] text-sm rounded-2xl p-1 z-[9999999] bg-white dark:bg-gray-850 dark:text-white shadow-lg border border-gray-100  dark:border-gray-800"
		sideOffset={-2}
		side="bottom"
		align="end"
		transition={flyAndScale}
	>
		<DropdownMenu.Item
			type="button"
			aria-pressed={($settings?.pinnedModels ?? []).includes(model?.id)}
			class="flex rounded-xl py-1.5 px-3 w-full hover:bg-gray-50 dark:hover:bg-gray-800 transition items-center gap-2"
			on:click={(e) => {
				e.stopPropagation();
				e.preventDefault();

				pinModelHandler(model?.id);
				show = false;
			}}
		>
			{#if ($settings?.pinnedModels ?? []).includes(model?.id)}
				<EyeSlash />
			{:else}
				<Eye />
			{/if}

			<div class="flex items-center">
				{#if ($settings?.pinnedModels ?? []).includes(model?.id)}
					{$i18n.t('Hide from Sidebar')}
				{:else}
					{$i18n.t('Keep in Sidebar')}
				{/if}
			</div>
		</DropdownMenu.Item>

		<DropdownMenu.Item
			type="button"
			class="flex rounded-xl py-1.5 px-3 w-full hover:bg-gray-50 dark:hover:bg-gray-800 transition items-center gap-2"
			on:click={(e) => {
				e.stopPropagation();
				e.preventDefault();

				copyLinkHandler();
				show = false;
			}}
		>
			<Link />

			<div class="flex items-center">{$i18n.t('Copy Link')}</div>
		</DropdownMenu.Item>

		<DropdownMenu.Item
			type="button"
			class="flex rounded-xl py-1.5 px-3 w-full hover:bg-gray-50 dark:hover:bg-gray-800 transition items-center gap-2"
			on:click={(e) => {
				e.stopPropagation();
				e.preventDefault();

				goto(`/admin/settings/models?id=${encodeURIComponent(model.id)}`);
				show = false;
			}}
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 16 16"
				fill="currentColor"
				class="size-4"
			>
				<path
					fill-rule="evenodd"
					d="M6.455 1.45A.5.5 0 0 1 6.952 1h2.096a.5.5 0 0 1 .497.45l.186 1.858a4.996 4.996 0 0 1 1.466.848l1.703-.769a.5.5 0 0 1 .639.206l1.047 1.814a.5.5 0 0 1-.14.656l-1.517 1.09a5.026 5.026 0 0 1 0 1.694l1.516 1.09a.5.5 0 0 1 .141.656l-1.047 1.814a.5.5 0 0 1-.639.206l-1.703-.768c-.433.36-.928.649-1.466.847l-.186 1.858a.5.5 0 0 1-.497.45H6.952a.5.5 0 0 1-.497-.45l-.186-1.858a4.993 4.993 0 0 1-1.466-.848l-1.703.769a.5.5 0 0 1-.639-.206l-1.047-1.814a.5.5 0 0 1 .14-.656l1.517-1.09a5.033 5.033 0 0 1 0-1.694l-1.516-1.09a.5.5 0 0 1-.141-.656L2.461 3.39a.5.5 0 0 1 .639-.206l1.703.768c.433-.36.928-.65 1.466-.847l.186-1.858Zm-.177 7.567-.003-.005A.75.75 0 0 1 6.5 8.75a.75.75 0 0 1 .225.262l.003.005L8 11.36l1.272-2.343.003-.005A.75.75 0 0 1 9.5 8.75a.75.75 0 0 1 .225.262l.003.005.003.004A1.5 1.5 0 1 1 8 11.5a1.5 1.5 0 1 1-1.731-2.48l.003-.004.006-.004Z"
					clip-rule="evenodd"
				/>
			</svg>

			<div class="flex items-center">{$i18n.t('Model Settings')}</div>
		</DropdownMenu.Item>
	</DropdownMenu.Content>
</DropdownMenu.Root>
