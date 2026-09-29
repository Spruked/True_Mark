import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import axios from "axios";
import { getActiveUser, getUserAuthHeaders, isUserAuthenticated } from "../authStorage";
import { getBackendApiBase } from "../apiBase";

const MintFlowContext = createContext(null);
const WORKSPACE_API = `${getBackendApiBase()}/api/workspace`;

const defaultWorkspace = {
  notes: "",
  links: "",
  checklist: "",
  draftSummary: null,
  paymentSession: null,
  updatedAt: null,
};

function buildSerializableDraft(draft) {
  if (!draft) {
    return null;
  }

  return {
    name: draft.name || "",
    email: draft.email || "",
    node_id: draft.node_id || "",
    region_code: draft.region_code || "",
    registrant_code: draft.registrant_code || "",
    prefix: draft.prefix || "",
    industry: draft.industry || "",
    nft_type: draft.nft_type || "",
    frame_id: draft.frame_id || "frame-01-engraved-single-line",
    package_tier: draft.package_tier || "p2",
    encryption: draft.encryption || "none",
    chain: draft.chain || "polygon",
    quantity: draft.quantity || 1,
    metadata: draft.metadata || "",
    payment_method: draft.payment_method || "fiat",
    fileName: draft.file?.name || draft.fileName || "",
    fileSize: draft.file?.size || draft.fileSize || 0,
    fileType: draft.file?.type || draft.fileType || "",
    hasLiveFile: Boolean(draft.file),
  };
}

export function MintFlowProvider({ children }) {
  const [checkoutDraft, setCheckoutDraft] = useState(null);
  const [workspace, setWorkspace] = useState(defaultWorkspace);

  useEffect(() => {
    async function hydrateWorkspace() {
      const activeUser = getActiveUser();

      if (!activeUser?.email || !isUserAuthenticated()) {
        setWorkspace(defaultWorkspace);
        setCheckoutDraft(null);
        return;
      }

      let storedWorkspace = null;
      try {
        const response = await axios.get(WORKSPACE_API, { headers: getUserAuthHeaders() });
        storedWorkspace = response.data;
      } catch {
        storedWorkspace = null;
      }

      if (!storedWorkspace) {
        setWorkspace(defaultWorkspace);
        setCheckoutDraft(null);
        return;
      }

      setWorkspace({
        ...defaultWorkspace,
        ...storedWorkspace,
      });

      if (storedWorkspace.draftSummary) {
        setCheckoutDraft(storedWorkspace.draftSummary);
      } else {
        setCheckoutDraft(null);
      }
    }

    void hydrateWorkspace();
    window.addEventListener("tm-auth-changed", hydrateWorkspace);

    return () => {
      window.removeEventListener("tm-auth-changed", hydrateWorkspace);
    };
  }, []);

  const persistWorkspace = async (nextWorkspace, nextDraft = checkoutDraft) => {
    const activeUser = getActiveUser();

    if (!activeUser?.email || !isUserAuthenticated()) {
      return;
    }

    try {
      await axios.put(WORKSPACE_API, {
        ...nextWorkspace,
        draftSummary: buildSerializableDraft(nextDraft),
        updatedAt: new Date().toISOString(),
      }, { headers: getUserAuthHeaders() });
    } catch {
      // The Vault API remains authoritative; callers retain in-memory state until it is available.
    }
  };

  const updateWorkspace = (updater) => {
    setWorkspace((currentWorkspace) => {
      const nextWorkspace = typeof updater === "function"
        ? updater(currentWorkspace)
        : {
            ...currentWorkspace,
            ...updater,
          };

      void persistWorkspace(nextWorkspace);
      return nextWorkspace;
    });
  };

  const setDraftAndPersist = (draft) => {
    setCheckoutDraft(draft);
      const nextWorkspace = {
        ...workspace,
        draftSummary: buildSerializableDraft(draft),
        updatedAt: new Date().toISOString(),
      };
    setWorkspace(nextWorkspace);
    void persistWorkspace(nextWorkspace, draft);
  };

  const clearDraftAndPersist = () => {
    setCheckoutDraft(null);
    const nextWorkspace = {
      ...workspace,
      draftSummary: null,
      updatedAt: new Date().toISOString(),
    };
    setWorkspace(nextWorkspace);
    void persistWorkspace(nextWorkspace, null);
  };

  const setPaymentSessionAndPersist = (paymentSession) => {
    const nextWorkspace = {
      ...workspace,
      paymentSession,
      updatedAt: new Date().toISOString(),
    };
    setWorkspace(nextWorkspace);
    void persistWorkspace(nextWorkspace);
  };

  const clearPaymentSessionAndPersist = () => {
    const nextWorkspace = {
      ...workspace,
      paymentSession: null,
      updatedAt: new Date().toISOString(),
    };
    setWorkspace(nextWorkspace);
    void persistWorkspace(nextWorkspace);
  };

  const value = useMemo(() => ({
    checkoutDraft,
    setCheckoutDraft: setDraftAndPersist,
    clearCheckoutDraft: clearDraftAndPersist,
    paymentSession: workspace.paymentSession || null,
    setPaymentSession: setPaymentSessionAndPersist,
    clearPaymentSession: clearPaymentSessionAndPersist,
    workspace,
    updateWorkspace,
  }), [checkoutDraft, workspace]);

  return (
    <MintFlowContext.Provider value={value}>
      {children}
    </MintFlowContext.Provider>
  );
}

export function useMintFlow() {
  const context = useContext(MintFlowContext);

  if (!context) {
    throw new Error("useMintFlow must be used within a MintFlowProvider.");
  }

  return context;
}
