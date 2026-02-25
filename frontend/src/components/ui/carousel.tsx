import * as React from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"

interface CarouselImage {
  id: number
  url: string
}

interface CarouselProps {
  images: CarouselImage[]
  alt?: string
  className?: string
  onImageClick?: (index: number) => void
}

function Carousel({ images, alt = "", className, onImageClick }: CarouselProps) {
  const [current, setCurrent] = React.useState(0)
  const containerRef = React.useRef<HTMLDivElement>(null)

  const goTo = (index: number) => {
    setCurrent(index)
    const container = containerRef.current
    if (container && container.children[index]) {
      (container.children[index] as HTMLElement).scrollIntoView({
        behavior: "smooth",
        block: "nearest",
        inline: "start",
      })
    }
  }

  const prev = () => goTo(Math.max(0, current - 1))
  const next = () => goTo(Math.min(images.length - 1, current + 1))

  // Detectar slide atual via IntersectionObserver no scroll
  React.useEffect(() => {
    const container = containerRef.current
    if (!container) return
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            const index = Array.from(container.children).indexOf(entry.target as Element)
            if (index >= 0) setCurrent(index)
          }
        }
      },
      { root: container, threshold: 0.5 }
    )
    Array.from(container.children).forEach((child) => observer.observe(child))
    return () => observer.disconnect()
  }, [images.length])

  if (images.length === 0) return null

  if (images.length === 1) {
    return (
      <img
        src={images[0].url}
        alt={alt}
        className={cn("w-full rounded-md object-contain", className)}
        onClick={() => onImageClick?.(0)}
        style={{ cursor: onImageClick ? "pointer" : undefined }}
      />
    )
  }

  return (
    <div className="relative group">
      {/* Container com scroll-snap */}
      <div
        ref={containerRef}
        className={cn(
          "flex snap-x snap-mandatory overflow-x-auto rounded-md",
          className
        )}
        style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
      >
        {images.map((img, i) => (
          <img
            key={img.id}
            src={img.url}
            alt={`${alt} ${i + 1}`}
            className="w-full flex-shrink-0 snap-center object-contain"
            style={{ cursor: onImageClick ? "pointer" : undefined }}
            onClick={() => onImageClick?.(i)}
          />
        ))}
      </div>

      {/* Seta esquerda */}
      {current > 0 && (
        <button
          type="button"
          onClick={(e) => { e.stopPropagation(); prev() }}
          className="absolute left-1 top-1/2 -translate-y-1/2 rounded-full bg-black/50 p-1 text-white opacity-0 transition-opacity group-hover:opacity-100 hover:bg-black/70"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
      )}

      {/* Seta direita */}
      {current < images.length - 1 && (
        <button
          type="button"
          onClick={(e) => { e.stopPropagation(); next() }}
          className="absolute right-1 top-1/2 -translate-y-1/2 rounded-full bg-black/50 p-1 text-white opacity-0 transition-opacity group-hover:opacity-100 hover:bg-black/70"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      )}

      {/* Bolinhas indicadoras */}
      <div className="absolute bottom-2 left-1/2 flex -translate-x-1/2 gap-1">
        {images.map((_, i) => (
          <button
            key={i}
            type="button"
            onClick={(e) => { e.stopPropagation(); goTo(i) }}
            className={cn(
              "h-1.5 w-1.5 rounded-full transition-colors",
              i === current ? "bg-white" : "bg-white/50"
            )}
          />
        ))}
      </div>
    </div>
  )
}

export { Carousel }
export type { CarouselImage }
