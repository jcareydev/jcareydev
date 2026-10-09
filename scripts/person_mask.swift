// Cut the person out of a photo using macOS's built-in Vision segmentation,
// so the portrait needs no downloaded background-removal model.
//
//     swift scripts/person_mask.swift <input image> <output mask.png>
//
// Writes a grayscale PNG the same size as the input: white = person.
import AppKit
import CoreImage
import Vision

let args = CommandLine.arguments
guard args.count == 3 else {
    FileHandle.standardError.write("usage: person_mask.swift <input> <output.png>\n".data(using: .utf8)!)
    exit(1)
}

let inURL = URL(fileURLWithPath: args[1])
let outURL = URL(fileURLWithPath: args[2])
guard let input = CIImage(contentsOf: inURL) else {
    FileHandle.standardError.write("could not read \(args[1])\n".data(using: .utf8)!)
    exit(1)
}

let request = VNGeneratePersonSegmentationRequest()
request.qualityLevel = .accurate
request.outputPixelFormat = kCVPixelFormatType_OneComponent8
try VNImageRequestHandler(ciImage: input).perform([request])

guard let buffer = request.results?.first?.pixelBuffer else {
    FileHandle.standardError.write("no person found\n".data(using: .utf8)!)
    exit(1)
}

// Vision returns a low-res mask; scale it back up to the photo's size.
var mask = CIImage(cvPixelBuffer: buffer)
mask = mask.transformed(by: CGAffineTransform(
    scaleX: input.extent.width / mask.extent.width,
    y: input.extent.height / mask.extent.height))

let context = CIContext()
try context.writePNGRepresentation(
    of: mask, to: outURL, format: .L8,
    colorSpace: CGColorSpace(name: CGColorSpace.linearGray)!)
print("wrote", outURL.path)
