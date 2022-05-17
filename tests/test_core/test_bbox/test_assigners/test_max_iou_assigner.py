# Copyright (c) OpenMMLab. All rights reserved.
"""Tests the Assigner objects.

CommandLine:
    pytest tests/test_utils/test_assigner.py
    xdoctest tests/test_utils/test_assigner.py zero
"""
import torch
from mmengine.data import InstanceData

from mmdet.core.bbox.assigners import MaxIoUAssigner


def test_max_iou_assigner():
    self = MaxIoUAssigner(
        pos_iou_thr=0.5,
        neg_iou_thr=0.5,
    )
    bboxes = torch.FloatTensor([
        [0, 0, 10, 10],
        [10, 10, 20, 20],
        [5, 5, 15, 15],
        [32, 32, 38, 42],
    ])
    gt_bboxes = torch.FloatTensor([
        [0, 0, 10, 9],
        [0, 10, 10, 19],
    ])
    gt_labels = torch.LongTensor([2, 3])

    pred_instances = InstanceData(bboxes=bboxes)
    gt_instances = InstanceData(bboxes=gt_bboxes, labels=gt_labels)

    assign_result = self.assign(pred_instances, gt_instances)
    assert len(assign_result.gt_inds) == 4
    assert len(assign_result.labels) == 4

    expected_gt_inds = torch.LongTensor([1, 0, 2, 0])
    assert torch.all(assign_result.gt_inds == expected_gt_inds)


def test_max_iou_assigner_with_ignore():
    self = MaxIoUAssigner(
        pos_iou_thr=0.5,
        neg_iou_thr=0.5,
        ignore_iof_thr=0.5,
        ignore_wrt_candidates=False,
    )
    bboxes = torch.FloatTensor([
        [0, 0, 10, 10],
        [10, 10, 20, 20],
        [5, 5, 15, 15],
        [30, 32, 40, 42],
    ])
    gt_bboxes = torch.FloatTensor([
        [0, 0, 10, 9],
        [0, 10, 10, 19],
    ])
    gt_bboxes_ignore = torch.Tensor([
        [30, 30, 40, 40],
    ])

    pred_instances = InstanceData(bboxes=bboxes)
    gt_instances = InstanceData(bboxes=gt_bboxes)
    gt_instances_ignore = InstanceData(bboxes=gt_bboxes_ignore)
    assign_result = self.assign(
        pred_instances, gt_instances, gt_instances_ignore=gt_instances_ignore)

    expected_gt_inds = torch.LongTensor([1, 0, 2, -1])
    assert torch.all(assign_result.gt_inds == expected_gt_inds)


def test_max_iou_assigner_with_empty_gt():
    """Test corner case where an image might have no true detections."""
    self = MaxIoUAssigner(
        pos_iou_thr=0.5,
        neg_iou_thr=0.5,
    )
    bboxes = torch.FloatTensor([
        [0, 0, 10, 10],
        [10, 10, 20, 20],
        [5, 5, 15, 15],
        [32, 32, 38, 42],
    ])
    gt_bboxes = torch.empty(0, 4)

    pred_instances = InstanceData(bboxes=bboxes)
    gt_instances = InstanceData(bboxes=gt_bboxes)
    assign_result = self.assign(pred_instances, gt_instances)

    expected_gt_inds = torch.LongTensor([0, 0, 0, 0])
    assert torch.all(assign_result.gt_inds == expected_gt_inds)


def test_max_iou_assigner_with_empty_boxes():
    """Test corner case where a network might predict no boxes."""
    self = MaxIoUAssigner(
        pos_iou_thr=0.5,
        neg_iou_thr=0.5,
    )
    bboxes = torch.empty((0, 4))
    gt_bboxes = torch.FloatTensor([
        [0, 0, 10, 9],
        [0, 10, 10, 19],
    ])
    gt_labels = torch.LongTensor([2, 3])

    pred_instances = InstanceData(bboxes=bboxes)
    gt_instances = InstanceData(bboxes=gt_bboxes, labels=gt_labels)
    # Test with gt_labels
    assign_result = self.assign(pred_instances, gt_instances)
    assert len(assign_result.gt_inds) == 0
    assert tuple(assign_result.labels.shape) == (0, )

    # Test without gt_labels
    gt_instances = InstanceData(bboxes=gt_bboxes)
    assign_result = self.assign(pred_instances, gt_instances)
    assert len(assign_result.gt_inds) == 0
    assert assign_result.labels is None


def test_max_iou_assigner_with_empty_boxes_and_ignore():
    """Test corner case where a network might predict no boxes and
    ignore_iof_thr is on."""
    self = MaxIoUAssigner(
        pos_iou_thr=0.5,
        neg_iou_thr=0.5,
        ignore_iof_thr=0.5,
    )
    bboxes = torch.empty((0, 4))
    gt_bboxes = torch.FloatTensor([
        [0, 0, 10, 9],
        [0, 10, 10, 19],
    ])
    gt_bboxes_ignore = torch.Tensor([
        [30, 30, 40, 40],
    ])
    gt_labels = torch.LongTensor([2, 3])

    pred_instances = InstanceData(bboxes=bboxes)
    gt_instances = InstanceData(bboxes=gt_bboxes, labels=gt_labels)
    gt_instances_ignore = InstanceData(bboxes=gt_bboxes_ignore)

    # Test with gt_labels
    assign_result = self.assign(
        pred_instances, gt_instances, gt_instances_ignore=gt_instances_ignore)
    assert len(assign_result.gt_inds) == 0
    assert tuple(assign_result.labels.shape) == (0, )

    # Test without gt_labels
    gt_instances = InstanceData(bboxes=gt_bboxes)
    assign_result = self.assign(
        pred_instances, gt_instances, gt_instances_ignore=gt_instances_ignore)
    assert len(assign_result.gt_inds) == 0
    assert assign_result.labels is None


def test_max_iou_assigner_with_empty_boxes_and_gt():
    """Test corner case where a network might predict no boxes and no gt."""
    self = MaxIoUAssigner(
        pos_iou_thr=0.5,
        neg_iou_thr=0.5,
    )
    bboxes = torch.empty((0, 4))
    gt_bboxes = torch.empty((0, 4))

    pred_instances = InstanceData(bboxes=bboxes)
    gt_instances = InstanceData(bboxes=gt_bboxes)
    assign_result = self.assign(pred_instances, gt_instances)
    assert len(assign_result.gt_inds) == 0