<script lang="ts">
	import { getContext, tick } from 'svelte';
	const i18n = getContext('i18n');

	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';
	import Cog6 from '$lib/components/icons/Cog6.svelte';
	import AddConnectionModal from '$lib/components/AddConnectionModal.svelte';
	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';

	export let onDelete = () => {};
	export let onSubmit = () => {};

	export let url = '';
	export let key = '';
	export let config = {};

	let showConfigModal = false;
	let showDeleteConfirmDialog = false;
</script>

<ConfirmDialog
	bind:show={showDeleteConfirmDialog}
	on:confirm={() => {
		onDelete();
	}}
/>

<AddConnectionModal
	edit
	gemini
	bind:show={showConfigModal}
	connection={{
		url,
		key,
		config
	}}
	onDelete={() => {
		showDeleteConfirmDialog = true;
	}}
	onSubmit={(connection) => {
		url = connection.url;
		key = connection.key;
		config = connection.config;
		onSubmit(connection);
	}}
/>

<div class="flex w-full gap-2 items-center">
	<Tooltip
		className="w-full relative"
		content={$i18n.t(`Gemini API Base URL: "{{url}}"`, {
			url
		})}
		placement="top-start"
	>
		{#if !(config?.enable ?? true)}
			<div
				class="absolute top-0 bottom-0 left-0 right-0 opacity-60 bg-white dark:bg-gray-900 z-10"
			></div>
		{/if}
		<div class="flex w-full gap-2">
			<div class="flex-1 relative">
				<input
					class=" outline-hidden w-full bg-transparent cursor-pointer"
					placeholder={$i18n.t('API Base URL')}
					value={config?.remark ? config.remark : url}
					autocomplete="off"
					readonly={true}
					on:click={() => {
						showConfigModal = true;
					}}
				/>

				<div class=" absolute top-0.5 right-2.5">
					<Tooltip content="Gemini API">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill="currentColor"
							class="size-4 text-blue-500"
						>
							<path
								d="M12 2L2 7v10l10 5 10-5V7L12 2zm0 18.54l-8-4V8.46l8 4v8.08zm8-4l-8 4v-8.08l8-4v8.08z"
							/>
						</svg>
					</Tooltip>
				</div>
			</div>
		</div>
	</Tooltip>

	<div class="flex gap-1">
		<Tooltip content={$i18n.t('Configure')} className="self-start">
			<button
				class="self-center p-1 bg-transparent hover:bg-gray-100 dark:bg-gray-900 dark:hover:bg-gray-850 rounded-lg transition"
				on:click={() => {
					showConfigModal = true;
				}}
				type="button"
			>
				<Cog6 />
			</button>
		</Tooltip>
	</div>
</div>
