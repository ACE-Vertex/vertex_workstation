import {
  useCallback,
  useRef,
  useState,
  type MouseEventHandler,
  type PointerEventHandler,
} from "react";

interface MiddleMouseScrollOptions {
  readonly axis?: "x" | "y" | "both";
  readonly ignoreFormControls?: boolean;
}

interface MiddleMouseScrollBindings {
  readonly onPointerDown: PointerEventHandler<HTMLElement>;
  readonly onPointerMove: PointerEventHandler<HTMLElement>;
  readonly onPointerUp: PointerEventHandler<HTMLElement>;
  readonly onPointerCancel: PointerEventHandler<HTMLElement>;
  readonly onAuxClick: MouseEventHandler<HTMLElement>;
  readonly "data-middle-scroll-active": "true" | "false";
}

function isFormControl(target: EventTarget | null): boolean {
  return (
    target instanceof HTMLElement &&
    Boolean(
      target.closest(
        "input, textarea, select, option, button, [contenteditable='true']",
      ),
    )
  );
}

export function useMiddleMouseScroll(
  options: MiddleMouseScrollOptions = {},
): MiddleMouseScrollBindings {
  const axis = options.axis ?? "y";
  const ignoreFormControls =
    options.ignoreFormControls ?? false;

  const origin = useRef({
    pointerId: -1,
    x: 0,
    y: 0,
    scrollLeft: 0,
    scrollTop: 0,
  });
  const [active, setActive] = useState(false);

  const finish = useCallback(
    (element: HTMLElement, pointerId: number) => {
      if (
        element.hasPointerCapture?.(pointerId)
      ) {
        element.releasePointerCapture(pointerId);
      }
      origin.current.pointerId = -1;
      setActive(false);
    },
    [],
  );

  const onPointerDown = useCallback<
    PointerEventHandler<HTMLElement>
  >(
    (event) => {
      if (event.button !== 1) return;

      if (
        ignoreFormControls &&
        isFormControl(event.target)
      ) {
        return;
      }

      event.preventDefault();

      const element = event.currentTarget;
      origin.current = {
        pointerId: event.pointerId,
        x: event.clientX,
        y: event.clientY,
        scrollLeft: element.scrollLeft,
        scrollTop: element.scrollTop,
      };

      element.setPointerCapture?.(event.pointerId);
      setActive(true);
    },
    [ignoreFormControls],
  );

  const onPointerMove = useCallback<
    PointerEventHandler<HTMLElement>
  >((event) => {
    if (
      !active ||
      origin.current.pointerId !== event.pointerId
    ) {
      return;
    }

    const element = event.currentTarget;
    const dx = event.clientX - origin.current.x;
    const dy = event.clientY - origin.current.y;

    if (axis === "x" || axis === "both") {
      element.scrollLeft =
        origin.current.scrollLeft - dx;
    }

    if (axis === "y" || axis === "both") {
      element.scrollTop =
        origin.current.scrollTop - dy;
    }
  }, [active, axis]);

  const onPointerUp = useCallback<
    PointerEventHandler<HTMLElement>
  >(
    (event) => {
      if (
        origin.current.pointerId === event.pointerId
      ) {
        finish(
          event.currentTarget,
          event.pointerId,
        );
      }
    },
    [finish],
  );

  const onPointerCancel = useCallback<
    PointerEventHandler<HTMLElement>
  >(
    (event) => {
      if (
        origin.current.pointerId === event.pointerId
      ) {
        finish(
          event.currentTarget,
          event.pointerId,
        );
      }
    },
    [finish],
  );

  const onAuxClick = useCallback<
    MouseEventHandler<HTMLElement>
  >((event) => {
    if (event.button === 1) {
      event.preventDefault();
    }
  }, []);

  return {
    onPointerDown,
    onPointerMove,
    onPointerUp,
    onPointerCancel,
    onAuxClick,
    "data-middle-scroll-active":
      active ? "true" : "false",
  };
}
